import flet as ft
import os
from openai import OpenAI
import requests
import base64

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = "아이디/레포이름"
APP_PASSWORD = os.environ.get("APP_PASSWORD")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def handle_image_upload(e, input_box, page):
    if e.files:
        file = e.files[0]

        input_box.value += "\n[이미지 분석 중...]"
        page.update()

        try:
            import base64

            with open(file.path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode()

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "이미지의 텍스트를 추출해줘"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                },
                            },
                        ],
                    }
                ],
            )

            extracted_text = response.choices[0].message.content

            input_box.value += f"\n[이미지 내용]\n{extracted_text}"

        except Exception as err:
            input_box.value += f"\n[이미지 처리 실패] {err}"

        page.update()

def handle_voice_upload(e, input_box, page):
    audio_file = e.files[0] if e.files else None
    
    if audio_file and hasattr(audio_file, 'path'):
        audio_file = audio_file.path

    print(audio_file)

    if not audio_file:
        input_box.value = "음성 파일이 선택되지 않았습니다"
        page.update()
        return

    input_box.value += "\n[음성 분석 중...]"
    page.update()

    try:
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f
            )

        input_box.value += f"\n[음성 내용]\n{transcript.text}"

    except Exception as err:
        input_box.value += f"\n[음성 처리 실패] {err}"

    page.update()


def generate_knowledge(text, client):
    prompt = f"""
당신은 옵시디언 기반 지식 시스템을 구축하는 전문가이다.

다음 내용을 지식 네트워크 문서로 변환하라:

{text}

조건:
- 폴더 경로 포함
- 제목 자동 생성
- 최소 3개 이상의 [[링크]]
- 태그 포함
- 마크다운 형식

출력 형식:
[저장 경로]
문서내용
링크목록
태그목록
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 지식 구조화 전문가다"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def generate_reading_knowledge(text, book_title, author, chapter, client):

    prompt = f"""
당신은 독서를 지식 네트워크로 변환하는 전문가이다.

다음 독서 내용을 분석하여 옵시디언 지식 문서로 변환하라:

[메타 정보]
책: {book_title}
저자: {author}
챕터: {chapter}

[내용]
{text}

---

반드시 아래를 수행하라:

1. 핵심 개념 2~3개 추출
2. 저자의 주장 구조 분석
3. 기존 개념과 연결 (추상 개념 포함)
4. 나의 적용 가능성 도출
5. 책 자체를 하나의 노드로 생성 [[{book_title}]]

---

출력 형식:

[저장 경로]

# 제목

## 핵심 개념

## 저자 주장 구조

## 나의 해석

## 적용 가능성

## 연결 개념

(여기에 [[링크]] 3~5개 생성)

---

태그도 생성하라
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 독서를 구조화하는 전문가다"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def save_to_obsidian(content):

    try:
        # GPT 결과에서 저장 경로 추출
        lines = content.split("\n")
        path_line = lines[0].strip()

        if "[저장 경로]" in path_line:
            file_path = path_line.replace("[저장 경로]", "").strip()
        else:
            file_path = "00 inbox/auto_note.md"

        file_path = file_path.replace("`", "")
        file_path = file_path.strip()

        if file_path.startswith("/"):
            file_path = file_path[1:]

        if file_path.endswith(".md"):
            file_path = file_path[:-3]

        file_path = file_path.replace(" ", "_")

        file_path = file_path + ".md"

        print("최종 저장 경로:", file_path)

        # 내용 인코딩
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"

        data = {
            "message": "auto note upload",
            "content": encoded_content
        }

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }

        response = requests.put(url, json=data, headers=headers)

        return response.status_code

    except Exception as e:
        return str(e)


def main(page: ft.Page):
    page.title = "Obsidian Capture"
    page.bgcolor = "#0f172a"
    page.padding = 20
    page.scroll = "auto"
    def build_main_ui():
        # 독서 모드 토글
        def toggle_reading_mode(e):
            is_mode_on = reading_mode_switch.value
            book_title.visible = is_mode_on
            author.visible = is_mode_on
            chapter.visible = is_mode_on
            page.update()

        reading_mode_switch = ft.Switch(label="독서 모드", value=False, on_change=toggle_reading_mode)

        book_title = ft.TextField(label="책 제목", bgcolor="#1e293b", color="white", visible=False)
        author = ft.TextField(label="저자", bgcolor="#1e293b", color="white", visible=False)
        chapter = ft.TextField(label="챕터 (선택)", bgcolor="#1e293b", color="white", visible=False)

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

        # 지식 생성
        def knowledge_click(e):
            try:
                if reading_mode_switch.value:
                    result = generate_reading_knowledge(
                        input_box.value, 
                        book_title.value, 
                        author.value, 
                        chapter.value, 
                        client
                    )
                else:
                    result = generate_knowledge(input_box.value, client)
                input_box.value = result
            except Exception as err:
                input_box.value = f"에러 발생: {err}"
            page.update()

        knowledge_btn = ft.ElevatedButton(
            "지식 생성",
            on_click=knowledge_click,
            bgcolor="#8b5cf6",
            color="white",
        )

        def obsidian_save_click(e):
            result = save_to_obsidian(input_box.value)
            if str(result).startswith("20"):
                page.snack_bar = ft.SnackBar(ft.Text("저장 완료"), bgcolor="#22c55e")
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"저장 실패: {result}"), bgcolor="#ef4444")
            page.snack_bar.open = True
            page.update()

        obsidian_save_btn = ft.ElevatedButton(
            "옵시디언 저장",
            on_click=obsidian_save_click,
            bgcolor="#14b8a6",
            color="white",
        )

        page.add(
            ft.Column(
                [
                    ft.Text("Obsidian Capture", size=28, color="white"),
                    reading_mode_switch,
                    book_title,
                    author,
                    chapter,
                    input_box,
                    ft.Row([image_btn, voice_btn], spacing=10),
                    ft.Row([save_btn, knowledge_btn, obsidian_save_btn], spacing=10)
                ]
            )
        )


    is_authenticated = False
    password_input = ft.TextField(password=True, bgcolor="#1e293b", color="white")

    def check_password(e):
        if password_input.value == APP_PASSWORD:
            page.session.set("auth", True)
            page.clean()
            build_main_ui()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("비밀번호 틀림"))
            page.snack_bar.open = True
            page.update()

    if page.session.get("auth"):
        build_main_ui()
    else:
        page.add(
            ft.Column([
                ft.Text("비밀번호 입력", size=20, color="white"),
                password_input,
                ft.ElevatedButton("로그인", on_click=check_password)
            ])
        )
ft.app(target=main, port=10000)
