import flet as ft

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

    # 이미지 업로드
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"{len(e.files)}개 이미지 선택됨")
            )
            page.snack_bar.open = True
            page.update()

    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)

    image_btn = ft.ElevatedButton(
        "📷 이미지 추가",
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        bgcolor="#334155",
        color="white",
    )

    # 음성 버튼 (현재는 UI만)
    def voice_click(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("🎤 음성 기능은 다음 단계에서 연결됩니다")
        )
        page.snack_bar.open = True
        page.update()

    voice_btn = ft.ElevatedButton(
        "🎤 음성 기록",
        on_click=voice_click,
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
