import os
import datetime
import shutil
import flet as ft
from openai import OpenAI

# User defined API key
OPENAI_API_KEY = "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"

def main(page: ft.Page):
    page.title = "Obsidian Capture"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 400
    page.window_height = 800

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # State variables
    audio_path = None
    image_path = None

    # Load previously saved vault path if available
    # Android Obsidian users usually mount their vault around /storage/emulated/0/Documents/Obsidian/...
    saved_vault_path = page.client_storage.get("vault_path") or "/storage/emulated/0/Documents/ObsidianVault"
    
    vault_path_input = ft.TextField(
        label="Obsidian Vault 경로", 
        value=saved_vault_path,
        hint_text="/storage/emulated/0/Documents/ObsidianVault",
        expand=True
    )

    text_input = ft.TextField(
        label="텍스트 내용 입력", 
        multiline=True, 
        min_lines=4,
        max_lines=8
    )

    status_text = ft.Text("대기 중...", color=ft.colors.GREY_400)

    def save_vault_path(e):
        page.client_storage.set("vault_path", vault_path_input.value)
        status_text.value = f"Vault 경로가 앱에 저장되었습니다."
        page.update()

    # File Pickers
    def on_audio_picked(e: ft.FilePickerResultEvent):
        nonlocal audio_path
        if e.files and len(e.files) > 0:
            audio_path = e.files[0].path
            btn_audio.text = f"음성 O ({e.files[0].name[:10]}...)"
            btn_audio.icon = ft.icons.CHECK_CIRCLE
            btn_audio.icon_color = ft.colors.GREEN_400
        else:
            audio_path = None
            btn_audio.text = "음성 파일 선택"
            btn_audio.icon = ft.icons.MIC
            btn_audio.icon_color = None
        page.update()

    def on_image_picked(e: ft.FilePickerResultEvent):
        nonlocal image_path
        if e.files and len(e.files) > 0:
            image_path = e.files[0].path
            btn_image.text = f"이미지 O ({e.files[0].name[:10]}...)"
            btn_image.icon = ft.icons.CHECK_CIRCLE
            btn_image.icon_color = ft.colors.GREEN_400
        else:
            image_path = None
            btn_image.text = "이미지 선택"
            btn_image.icon = ft.icons.IMAGE
            btn_image.icon_color = None
        page.update()

    audio_picker = ft.FilePicker(on_result=on_audio_picked)
    image_picker = ft.FilePicker(on_result=on_image_picked)
    page.overlay.extend([audio_picker, image_picker])

    btn_audio = ft.ElevatedButton(
        "음성 파일 선택",
        icon=ft.icons.MIC,
        on_click=lambda _: audio_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.AUDIO),
        expand=True
    )

    btn_image = ft.ElevatedButton(
        "이미지 선택",
        icon=ft.icons.IMAGE,
        on_click=lambda _: image_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE),
        expand=True
    )

    def process_capture(e):
        # Disable button to prevent multi-clicks
        process_btn.disabled = True
        page.update()

        try:
            vault_base = vault_path_input.value.strip()
            if not vault_base:
                status_text.value = "Error: Vault 경로를 상단에 입력해주세요."
                return
                
            assets_path = os.path.join(vault_base, "99 assets")
            output_path = os.path.join(vault_base, "00 inbox")

            status_text.value = "폴더 구조 확인 및 생성 중..."
            page.update()

            # Ensure directories exist
            os.makedirs(assets_path, exist_ok=True)
            os.makedirs(output_path, exist_ok=True)

            # 1. 음성 -> 텍스트 (OpenAI API)
            transcript = ""
            nonlocal audio_path
            if audio_path:
                status_text.value = "음성 텍스트 변환 중 (OpenAI Whisper)..."
                page.update()
                
                with open(audio_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file
                    )
                transcript = transcription.text

            # 2. 이미지 복사
            image_md = ""
            nonlocal image_path
            if image_path:
                status_text.value = "이미지 복사 중..."
                page.update()
                
                filename = os.path.basename(image_path)
                # 중복 방지를 위한 타임스탬프 추가
                timestamp = datetime.datetime.now().strftime('%H%M%S_')
                new_filename = timestamp + filename
                dest = os.path.join(assets_path, new_filename)
                
                shutil.copy(image_path, dest)
                image_md = f"![[{new_filename}]]"

            # 3. 간단 제목 생성 (텍스트가 없으면 Date 기반 생성)
            input_text_val = text_input.value.strip()
            title = (input_text_val[:20] if input_text_val else "capture").replace("\n", " ").strip()
            if not title:
                title = "capture"

            # 4. 마크다운 내용 구성
            content = f"# {title}\n\n## 텍스트\n{input_text_val}\n\n## 음성\n{transcript}\n\n## 이미지\n{image_md}\n\n## 연결\n[[자동화]] [[기록]] [[지식]]\n"

            # 5. 저장
            file_ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            # 파일이름 제약 처리 (특수문자 제거)
            safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
            md_filename = f"{file_ts}_{safe_title}.md"
            filepath = os.path.join(output_path, md_filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            status_text.value = f"저장 완료: {md_filename}"
            
            # Reset UI loosely
            text_input.value = ""
            btn_audio.text = "음성 파일 선택"
            btn_audio.icon = ft.icons.MIC
            btn_audio.icon_color = None
            btn_image.text = "이미지 선택"
            btn_image.icon = ft.icons.IMAGE
            btn_image.icon_color = None
            audio_path = None
            image_path = None
            
        except Exception as ex:
            status_text.value = f"에러 발생: {str(ex)}"
        finally:
            process_btn.disabled = False
            page.update()


    process_btn = ft.ElevatedButton(
        "기록 → 옵시디언 저장하기", 
        icon=ft.icons.SAVE,
        on_click=process_capture,
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
        height=50
    )

    save_path_btn = ft.IconButton(
        icon=ft.icons.SAVE_ALT,
        icon_color=ft.colors.BLUE_400,
        tooltip="경로 앱에 저장하기",
        on_click=save_vault_path
    )

    # Layout construction
    page.add(
        ft.Row([
            ft.Icon(ft.icons.EDIT_DOCUMENT, color=ft.colors.PURPLE_400, size=30),
            ft.Text("Obsidian Mobile Capture", size=24, weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Divider(),
        
        ft.Row([vault_path_input, save_path_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=10),
        text_input,
        
        ft.Container(height=10),
        ft.Row([btn_audio, btn_image], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=20),
        ft.Row([process_btn], alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Container(height=10),
        ft.Row([status_text], alignment=ft.MainAxisAlignment.CENTER)
    )
    page.add(ft.Text("앱 실행 성공"))

if __name__ == "__main__":
    ft.app(target=main, port=10000)
