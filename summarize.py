"""Claudeを使って書籍のMarkdown要約資料を生成する。"""
from pathlib import Path

from .client import get_client, get_model
from .extract import Chapter, extract_book

CHAPTER_SUMMARY_PROMPT = """以下は書籍の一部（{title}）です。日本語で、次の形式でMarkdownの要約を作成してください。

## {title}

**要点（箇条書き3〜6個）**
- ...

**キーコンセプト・用語**
- ...

本文:
{text}
"""

OVERVIEW_PROMPT = """以下は書籍の各章の要約です。これらを踏まえて、本全体の要約を日本語のMarkdownで作成してください。
含めるべき内容：
- 本のテーマ・主張の要約（3〜5文）
- 全体を通じたキーとなる考え方（箇条書き）
- 実務・生活への活かし方の提案（箇条書き）

各章の要約:
{summaries}
"""

MAX_CHARS_PER_REQUEST = 60000


def _ask(client, model: str, prompt: str) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def summarize_chapter(client, model: str, chapter: Chapter) -> str:
    text = chapter.text[:MAX_CHARS_PER_REQUEST]
    prompt = CHAPTER_SUMMARY_PROMPT.format(title=chapter.title, text=text)
    return _ask(client, model, prompt)


def summarize_book(path: Path, output_dir: Path) -> Path:
    client = get_client()
    model = get_model()

    chapters = extract_book(path)
    if not chapters:
        raise RuntimeError("本文を抽出できませんでした。ファイルを確認してください。")

    print(f"{len(chapters)}個のセクションを検出しました。要約を生成します...")
    chapter_summaries = []
    for i, chapter in enumerate(chapters, start=1):
        print(f"  [{i}/{len(chapters)}] {chapter.title} を要約中...")
        chapter_summaries.append(summarize_chapter(client, model, chapter))

    print("本全体のまとめを生成中...")
    combined = "\n\n".join(chapter_summaries)[:MAX_CHARS_PER_REQUEST]
    overview = _ask(client, model, OVERVIEW_PROMPT.format(summaries=combined))

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{path.stem}_summary.md"
    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"# {path.stem}\n\n")
        f.write("## 全体まとめ\n\n")
        f.write(overview.strip() + "\n\n")
        f.write("---\n\n")
        f.write("## 章ごとの要約\n\n")
        f.write("\n\n".join(chapter_summaries))

    return out_path
