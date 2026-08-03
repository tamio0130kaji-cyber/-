"""本の内容についてAIと対話するチャットモード。"""
from pathlib import Path

from .client import get_client, get_model
from .extract import extract_book

MAX_CONTEXT_CHARS = 500000  # ざっくり200kトークン程度を上限の目安に

SYSTEM_PROMPT_TEMPLATE = """あなたは読書アシスタントです。以下は「{title}」という本の本文です。
ユーザーはこの本の内容について質問したり相談したりします。本文の内容に基づいて、日本語で具体的かつ簡潔に答えてください。
本文にない内容を聞かれた場合は、本文からは分からない旨を伝えた上で一般的な知識で補足してください。

--- 本文ここから ---
{content}
--- 本文ここまで ---
"""


def chat_with_book(path: Path) -> None:
    client = get_client()
    model = get_model()

    print("本文を読み込んでいます...")
    chapters = extract_book(path)
    full_text = "\n\n".join(c.text for c in chapters)

    if len(full_text) > MAX_CONTEXT_CHARS:
        print("※ 本文が長いため、末尾を切り詰めてAIに渡します。")
        full_text = full_text[:MAX_CONTEXT_CHARS]

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(title=path.stem, content=full_text)

    history: list[dict] = []
    print(f"「{path.stem}」について質問できます。終了するには exit と入力してください。\n")

    while True:
        try:
            question = input("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        history.append({"role": "user", "content": question})

        print("AI: ", end="", flush=True)
        answer_parts = []
        with client.messages.stream(
            model=model,
            max_tokens=1500,
            system=system_prompt,
            messages=history,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                answer_parts.append(text)
        print("\n")

        history.append({"role": "assistant", "content": "".join(answer_parts)})
