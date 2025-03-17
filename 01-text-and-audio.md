# Gemini Multimodal Live API ハンズオン その 1

## 始めましょう

この手順では Google Gen AI SDK を使い、テキストを入力して Gemini モデルと対話、テキストまたは音声で応答を得る方法を確認します。

<walkthrough-tutorial-duration duration="30"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="1"></walkthrough-tutorial-difficulty>

**前提条件**:

- Google Cloud 上にプロジェクトが作成してある
- プロジェクトの _編集者_ 相当の権限をもつユーザーでログインしている
- _プロジェクト IAM 管理者_ 相当の権限をもつユーザーでログインしている
- (推奨) Google Chrome を利用している

**[開始]** ボタンをクリックして次のステップに進みます。

## プロジェクトの設定

この手順の中で実際にリソースを構築する対象のプロジェクトを選択してください。

<walkthrough-project-setup></walkthrough-project-setup>

## 1. エディタの起動

[Cloud Shell エディタ](https://cloud.google.com/shell/docs/launching-cloud-shell-editor?hl=ja) は個人ごとに割り当てられる開発環境としてご利用いただけます。Cloud Shell エディタを起動してみましょう。

```bash
cloudshell workspace gemini-multimodal-live-api-handson
```

Cloud Shell エディタが開いたら  
<walkthrough-editor-spotlight spotlightId="file-explorer">explorer view</walkthrough-editor-spotlight> でファイルの一覧を確認しましょう。

## 2. CLI の初期設定 & API の有効化

gcloud（[Google Cloud の CLI ツール](https://cloud.google.com/sdk/gcloud?hl=ja) のデフォルト プロジェクトを設定します。

```bash
export GOOGLE_CLOUD_PROJECT=<walkthrough-project-id/>
```

```bash
gcloud config set project "${GOOGLE_CLOUD_PROJECT}"
```

[Vertex AI](https://cloud.google.com/vertex-ai?hl=ja) など、関連サービスを有効化し、利用できる状態にします。

```bash
gcloud services enable aiplatform.googleapis.com compute.googleapis.com run.googleapis.com artifactregistry.googleapis.com iamcredentials.googleapis.com cloudresourcemanager.googleapis.com
```

みなさんの権限でアプリケーションを動作させるため、アプリケーションのデフォルト認証情報（ADC）を作成します。  
表示される URL をブラウザの別タブで開き、認証コードをコピー、ターミナルに貼り付け Enter を押してください。

```bash
mkdir -p $HOME/.config/gcloud/
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/application_default_credentials.json
```

```bash
gcloud auth application-default login --quiet
```

```bash
mv /tmp/*/application_default_credentials.json $HOME/.config/gcloud/ > /dev/null 2>&1
```

認証情報が生成されたことを確かめます。

```bash
cat ${GOOGLE_APPLICATION_CREDENTIALS} | jq .
```

## 3. ローカル Python 環境のセットアップ

venv を使って仮想環境を作成します。

```bash
python -m venv .venv
source .venv/bin/activate
```

Python 版 Gen AI SDK をインストールしましょう。

```bash
pip install google-genai
```

## 4. Gemini Multimodal Live API とは

Multimodal Live API の主な機能は次のとおりです。

- **マルチモダリティ**: モデルは、見て、聞いて、会話できます。
- **低遅延のリアルタイム インタラクション**: モデルは、すばやくレスポンスを返すことができます。
- **セッション メモリ**: モデルは、1 つのセッションで行われたすべてのやりとりを記憶し、以前に聞いたことや見たことがある情報を思い出すことができます。
- **関数呼び出しやコード実行のサポート**: モデルを外部サービスやデータソースと統合できます。

これらは [WebSocket](https://ja.wikipedia.org/wiki/WebSocket) を使ったステートフルな API として実装されています。

WebSocket はアプリと API を常に繋いでおく技術で、ある意味では電話のようなものです。一度繋がればお互いに好きなタイミングで情報を送り合えますし、電話を切るまでは相手とのやりとりをお互い記憶することも容易です。一方、必要な時にだけ情報を取りに行く対比的な方法として、REST API というものもあります。例えるなら駅の切符発券機のようなイメージです。行きたい場所のボタンを押せば切符が出てきますが、発券機はあなたのことを覚えていませんし、発券機側から何かを発信することもありません。リアルタイムかつ継続的なやり取りには電話 (WebSocket)、必要な情報をその都度得るには切符発券機 (REST API) のような技術が向いています。

## 5. サンプル: テキスト → テキスト

何はともあれ、まずはサンプルコードを読んでみましょう。  
<walkthrough-editor-open-file filePath="src/01/01-text-to-text.py">01-text-to-text.py</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/01/01-text-to-text.py" startLine="19" endLine="19" startCharacterOffset="11" endCharacterOffset="100">L.20</walkthrough-editor-select-line> では Multimodal Live API が利用できる `gemini-2.0-flash-001` を指定しています。
- <walkthrough-editor-select-line filePath="src/01/01-text-to-text.py" startLine="27" endLine="27" startCharacterOffset="4" endCharacterOffset="100">L.28</walkthrough-editor-select-line> の `genai.Client()` は Google の生成 AI クライアントを初期化しています。
- <walkthrough-editor-select-line filePath="src/01/01-text-to-text.py" startLine="30" endLine="30" startCharacterOffset="4" endCharacterOffset="14">L.31</walkthrough-editor-select-line> `async with` を使用することで、接続の開始と終了が自動的に管理されます。
- <walkthrough-editor-select-line filePath="src/01/01-text-to-text.py" startLine="43" endLine="43" startCharacterOffset="8" endCharacterOffset="100">L.44</walkthrough-editor-select-line> 非同期的にサーバーからの入力を受け付けます。
- <walkthrough-editor-select-line filePath="src/01/01-text-to-text.py" startLine="53" endLine="53" startCharacterOffset="4" endCharacterOffset="100">L.54</walkthrough-editor-select-line> `asyncio` パッケージを使うことで効率的に非同期処理を管理します。

このコードを実行するための認証はすでに済んでいますが、Multimodal Live API は現在 Preview 中で、Iowa など限られたリージョンでのみ利用できる点に注意が必要です。また、Google Cloud の利用規約を前提とした API 利用ができるよう Vertex AI 経由とします。

いずれも環境変数として設定しておきましょう。

```bash
export GOOGLE_GENAI_USE_VERTEXAI=True
export GOOGLE_CLOUD_LOCATION=us-central1
```

準備ができたので、実行してみましょう。

```bash
python src/01/01-text-to-text.py
```

## 6. サンプル: テキスト → 音声

サンプルコードを読んでみましょう。  
<walkthrough-editor-open-file filePath="src/01/02-text-to-audio.py">02-text-to-audio.py</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/01/02-text-to-audio.py" startLine="60" endLine="60" startCharacterOffset="13" endCharacterOffset="54">L.61</walkthrough-editor-select-line> 音声での応答を指示します。
- <walkthrough-editor-select-line filePath="src/01/02-text-to-audio.py" startLine="61" endLine="63" startCharacterOffset="0" endCharacterOffset="100">L.62</walkthrough-editor-select-line> 日本語での応答を "システム指示" として設定しています。このように指定すると、都度プロンプトでお願いする必要がなくなります。
- <walkthrough-editor-select-line filePath="src/01/02-text-to-audio.py" startLine="86" endLine="86" startCharacterOffset="20" endCharacterOffset="50">L.87</walkthrough-editor-select-line> 応答をファイルに書き込みます。

実行してみましょう。

```bash
python src/01/02-text-to-audio.py
```

音声を聞くために iPython ノートブックを使います。ipykernel をインストールしましょう。

```bash
pip install ipykernel
```

音声ファイルを移動して

```bash
mv audio.wav src/01/ > /dev/null 2>&1
```

audio-player.ipynb ファイルを開きましょう。その上で・・

1. ポップアップで "Do you want to install the recommended 'Jupyter' extension .." などと表示されます。Jupyter 拡張をインストールしてください。
2. その上で画面右上の "Select Kernel" から、実行環境として `Python Environment` > `Python 3.12.3` などを選択し
3. `Run All` ボタン、または三角ボタンを押して、コードを実行してください。

音声は流れましたか？

## その 1 はこれで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

では続けて、ハンズオン その 2 へ進みましょう！

```bash
teachme 02-audio-to-audio.md
```
