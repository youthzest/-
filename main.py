import flet as ft
import pytesseract
from PIL import Image

def handle_image_upload(e, input_box, page):
    if e.files:
        file = e.files[0]
        try:
            text = pytesseract.image_to_string(Image.open(file.path))
            input_box.value += f"\n[이미지 내용]\n{text}"
        except:
            input_box.value += "\n[이미지 처리 실패]"
        page.update()

def handle_voice_upload(e, input_box, page):
    if e.files:
        input_box.value += "\n[음성 파일 업로드 완료]"
        input_box.value += "\n[음성 → 텍스트 변환은 다음 단계에서 연결]"
        page.update()


def main(page: ft.Page):
    page.title = "Obsidian Capture"
    page.bgcolor = "#0f172a"
    page.padding = 20
    page.scroll = "auto"

    # 텍스트 입력
    input_box = ft.TextField(
        hint_text="여기에 기록하세요...",
        multiline=True,
        min_lines=5,
        max_lines=10,
        bgcolor="#1e293b",
        color="white",
    )

    # 이미지 파일 선택창
    image_picker = ft.FilePicker(on_result=lambda e: handle_image_upload(e, input_box, page))
    page.overlay.append(image_picker)

    image_btn = ft.ElevatedButton(
        "📷 이미지 추가",
        on_click=lambda _: image_picker.pick_files(allow_multiple=False),
        bgcolor="#334155",
        color="white",
    )

    # 음성 파일 선택창
    voice_picker = ft.FilePicker(on_result=lambda e: handle_voice_upload(e, input_box, page))
    page.overlay.append(voice_picker)

    voice_btn = ft.ElevatedButton(
        "🎤 음성 기록",
        on_click=lambda _: voice_picker.pick_files(allow_multiple=False),
        bgcolor="#334155",
        color="white",
    )

    # 저장
    def save_click(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("저장 완료"),
            bgcolor="#22c55e"
        )
        page.snack_bar.open = True
        page.update()

    save_btn = ft.ElevatedButton(
        "저장하기",
        on_click=save_click,
        bgcolor="#3b82f6",
        color="white",
    )

    page.add(
        ft.Column(
            [
                ft.Text("Obsidian Capture", size=28, color="white"),
                input_box,
                ft.Row([image_btn, voice_btn], spacing=10),
                save_btn
            ]
        )
    )

ft.app(target=main, port=10000)
