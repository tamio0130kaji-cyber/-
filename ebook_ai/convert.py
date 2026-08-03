"""DRMフリーの電子書籍（EPUB）を読みやすいPDFに変換する。

対象はDRMのかかっていないEPUBのみ。DRM付き電子書籍のPDF化（スクリーンショット
の自動取得など保護回避を目的とした手法）は著作権法上の理由によりサポートしない。
"""
from html import escape
from pathlib import Path

from .extract import extract_book

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<style>
  @page {{ size: A5; margin: 18mm 15mm; }}
  body {{
    font-family: "Hiragino Mincho ProN", "Hiragino Sans", "Yu Mincho", serif;
    line-height: 1.9;
    font-size: 11pt;
  }}
  h1 {{ font-size: 18pt; margin-bottom: 1.5em; }}
  h2 {{
    font-size: 13pt;
    margin-top: 2em;
    border-bottom: 1px solid #333;
    padding-bottom: 0.3em;
    page-break-before: always;
  }}
  p {{ white-space: pre-wrap; margin: 0.8em 0; }}
</style>
</head>
<body>
<h1>{title}</h1>
{chapters}
</body>
</html>
"""

CHAPTER_TEMPLATE = "<h2>{title}</h2>\n<p>{text}</p>\n"


def convert_to_pdf(path: Path, output_dir: Path) -> Path:
    if path.suffix.lower() != ".epub":
        raise ValueError("to-pdf はDRMフリーのEPUBファイルのみ対応しています。")

    chapters = extract_book(path)
    if not chapters:
        raise RuntimeError("本文を抽出できませんでした。ファイルを確認してください。")

    chapters_html = "\n".join(
        CHAPTER_TEMPLATE.format(
            title=escape(c.title),
            text=escape(c.text).replace("\n", "</p>\n<p>"),
        )
        for c in chapters
    )
    html = HTML_TEMPLATE.format(title=escape(path.stem), chapters=chapters_html)

    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise RuntimeError(
            "PDF変換にはweasyprintが必要です。READMEのセットアップ手順"
            "（brew install pango と pip install -r requirements.txt）を実行してください。"
        ) from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{path.stem}.pdf"
    HTML(string=html).write_pdf(str(out_path))
    return out_path
