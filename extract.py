"""EPUB / PDFから章単位でテキストを抽出する。

対応するのはDRM（コピー防止）のかかっていない電子書籍のみ。
DRM解除機能は著作権法上の理由により提供しない。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT
from pypdf import PdfReader

PDF_PAGES_PER_CHAPTER = 15


@dataclass
class Chapter:
    title: str
    text: str


def extract_epub(path: Path) -> list[Chapter]:
    book = epub.read_epub(str(path))
    chapters: list[Chapter] = []
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text = soup.get_text("\n", strip=True)
        if not text:
            continue
        heading = soup.find(["h1", "h2", "h3"])
        title = heading.get_text(strip=True) if heading else f"セクション {len(chapters) + 1}"
        chapters.append(Chapter(title=title, text=text))
    return chapters


def extract_pdf(path: Path) -> list[Chapter]:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]

    chapters: list[Chapter] = []
    for start in range(0, len(pages), PDF_PAGES_PER_CHAPTER):
        end = min(start + PDF_PAGES_PER_CHAPTER, len(pages))
        text = "\n".join(pages[start:end]).strip()
        if not text:
            continue
        chapters.append(Chapter(title=f"{start + 1}〜{end}ページ", text=text))
    return chapters


def extract_book(path: Path) -> list[Chapter]:
    suffix = path.suffix.lower()
    if suffix == ".epub":
        return extract_epub(path)
    if suffix == ".pdf":
        return extract_pdf(path)
    raise ValueError(f"対応していないファイル形式です: {suffix}（EPUBまたはPDFのみ対応）")
