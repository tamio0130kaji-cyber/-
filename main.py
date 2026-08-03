"""ebook-ai CLI — 電子書籍をAIで資料化・相談するツール（Mac向け）"""
import argparse
import sys
from pathlib import Path

from ebook_ai.chat import chat_with_book
from ebook_ai.convert import convert_to_pdf
from ebook_ai.extract import extract_book
from ebook_ai.summarize import summarize_book

OUTPUT_DIR = Path("output")


def cmd_extract(args):
    path = Path(args.file)
    chapters = extract_book(path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{path.stem}.txt"
    with out_path.open("w", encoding="utf-8") as f:
        for chapter in chapters:
            f.write(f"# {chapter.title}\n\n{chapter.text}\n\n")
    print(f"抽出したテキストを {out_path} に保存しました（{len(chapters)}セクション）。")


def cmd_summarize(args):
    path = Path(args.file)
    out_path = summarize_book(path, OUTPUT_DIR)
    print(f"要約資料を {out_path} に保存しました。")


def cmd_chat(args):
    path = Path(args.file)
    chat_with_book(path)


def cmd_to_pdf(args):
    path = Path(args.file)
    if path.suffix.lower() == ".pdf":
        print("入力がすでにPDFです。変換の必要はありません。")
        return
    out_path = convert_to_pdf(path, OUTPUT_DIR)
    print(f"PDFを {out_path} に保存しました。")


def main():
    parser = argparse.ArgumentParser(
        description="電子書籍（EPUB/PDF、DRMフリーのもの）をAIで資料化・相談するツール"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract", help="本文をテキストとして抽出する")
    p_extract.add_argument("file", help="EPUBまたはPDFファイルのパス")
    p_extract.set_defaults(func=cmd_extract)

    p_summarize = sub.add_parser("summarize", help="章ごとの要約とMarkdown資料を生成する")
    p_summarize.add_argument("file", help="EPUBまたはPDFファイルのパス")
    p_summarize.set_defaults(func=cmd_summarize)

    p_chat = sub.add_parser("chat", help="本の内容についてAIと対話する")
    p_chat.add_argument("file", help="EPUBまたはPDFファイルのパス")
    p_chat.set_defaults(func=cmd_chat)

    p_to_pdf = sub.add_parser("to-pdf", help="EPUB（DRMフリー）を読みやすいPDFに自動変換する")
    p_to_pdf.add_argument("file", help="EPUBファイルのパス")
    p_to_pdf.set_defaults(func=cmd_to_pdf)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:  # noqa: BLE001
        print(f"エラー: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
