import flet as ft

def main(page: ft.Page):
    page.title = "Obsidian Capture"
    page.bgcolor = "#0f172a"
    page.padding = 20
    page.scroll = "auto"

    # 타이틀
    title = ft.Text(
        "Obsidian Capture",
        size=28,
        weight="bold",
        color="white"
    )

    subtitle = ft.Text(
        "생각을 기록하고 정리하세요",
        size=14,
        color="#94a3b8"
    )

    # 입력창
    input_box = ft.TextField(
        hint_text="여기에 생각을 기록하세요...",
        multiline=True,
        min_lines=5,
        max_lines=10,
        border_radius=12,
        bgcolor="#1e293b",
        color="white",
    )

    # 버튼
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
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=15,
        ),
        bgcolor="#3b82f6",
        color="white",
    )

    # 카드 레이아웃
    card = ft.Container(
        content=ft.Column(
            [
                title,
                subtitle,
                ft.Divider(color="#334155"),
                input_box,
                save_btn,
            ],
            spacing=15,
        ),
        padding=20,
        border_radius=16,
        bgcolor="#1e293b",
    )

    # 중앙 정렬
    page.add(
        ft.Column(
            [
                ft.Container(height=20),
                card
            ],
            alignment="center",
        )
    )

ft.app(target=main, port=10000)
