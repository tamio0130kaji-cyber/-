# ebook-ai — 電子書籍をAIで資料化・相談するMac用ツール

購入した電子書籍（EPUB / PDF）をClaude AIに読み込ませ、

1. 章ごとの要約とMarkdown資料を自動生成する（`summarize`）
2. 本の内容を踏まえてAIと対話・相談する（`chat`）

ための、Mac上で動くシンプルなコマンドラインツールです。

## 重要：対応できる電子書籍について（著作権法上の注意）

このツールは **DRM（コピー防止）がかかっていない EPUB / PDF** のみを対象にしています。

- 対応できる例：青空文庫などのフリーEPUB、DRMフリーで販売されている本、自分でスキャン・PDF化した本など
- 対応できない例：KindleなどDRMがかかっている電子書籍

日本の著作権法では、私的利用であっても電子書籍のDRM（技術的保護手段）を回避することは違法とされているため、本ツールにはDRM解除機能は含まれておらず、今後も追加しません。DRM付きの本を活用したい場合は、出版社が提供する正規の書き出し機能や、朗読音声からの文字起こしなど、著作権法の範囲内の方法を別途検討してください。

## セットアップ（Mac）

```bash
# 1. 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. Anthropic APIキーを設定
cp .env.example .env
# .env を開いて ANTHROPIC_API_KEY=sk-ant-xxxx を記入
```

Anthropic APIキーは https://console.anthropic.com で発行できます。

## 使い方

### 1. 要約・資料化

```bash
python main.py summarize path/to/book.epub
# もしくは
python main.py summarize path/to/book.pdf
```

`output/` フォルダに `<本の名前>_summary.md` が生成されます。章ごとの要点箇条書き・キーコンセプトと、本全体のまとめが含まれます。

### 2. 本について対話・相談する

```bash
python main.py chat path/to/book.epub
```

本文全体をAIに読み込ませた状態で、ターミナル上でチャットが始まります（`exit` または `quit` で終了）。

```
あなた: この本で著者が一番伝えたい主張は？
AI: ...
あなた: 第3章の考え方を仕事にどう活かせますか？
AI: ...
```

### 3. EPUB（DRMフリー）を自動でPDF化する

```bash
python main.py to-pdf path/to/book.epub
```

`output/` フォルダに読みやすいレイアウトの `<本の名前>.pdf` が生成されます（章ごとに改ページ）。
対応するのはDRMのかかっていないEPUBのみです。KindleなどDRM付きの本のスクリーンショット取得によるPDF化のような、保護回避を目的とした自動化は著作権法上の理由によりサポートしません。

PDF変換にはmacOSに以下のライブラリが必要です（初回のみ）：

```bash
brew install pango
```

### 4. テキスト抽出だけ行う（下ごしらえ）

```bash
python main.py extract path/to/book.epub
```

`output/` に章分割済みのプレーンテキストが出力されます。他のツールに読み込ませたい場合などに使えます。

## 仕組み

- EPUBは章（spine）ごとに、PDFはページ単位のまとまりごとにテキストを抽出します。
- `summarize` は章ごとにClaudeへ要約を依頼し、最後に全章の要約から本全体のまとめを生成します（長い本でも1回のリクエストに収まるよう分割処理）。
- `chat` は抽出した本文全体をコンテキストとしてClaudeに渡し、対話履歴を保持しながら質問に答えます。極端に長い本（数十万文字超）の場合は末尾が切り詰められる旨を警告表示します。

## 使用モデルの変更

デフォルトは `claude-sonnet-5` です。`.env` に `CLAUDE_MODEL=claude-opus-5` のように指定すると変更できます。
