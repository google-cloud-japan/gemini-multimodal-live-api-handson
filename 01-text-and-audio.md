# Gemini Multimodal Live API ハンズオン その 1

## 始めましょう

この手順では Google Gen AI SDK を使い、テキストを入力して Gemini モデルと対話、テキストまたは音声で応答を得る方法を確認します。

**前提条件**:

- Google Cloud 上にプロジェクトが作成してある
- プロジェクトの _編集者_ 相当の権限をもつユーザーでログインしている
- _プロジェクト IAM 管理者_ 相当の権限をもつユーザーでログインしている
- (推奨) Google Chrome を利用している

## 1. CLI の初期設定 & API の有効化

gcloud（Google Cloud の CLI ツール) を[こちらの方法でインストール](https://cloud.google.com/sdk/docs/install-sdk?hl=ja) し、以下のコマンドにあなたの **プロジェクト ID** を指定し、実行してください。

```bash
export GOOGLE_CLOUD_PROJECT=
```

```bash
gcloud config set project "${GOOGLE_CLOUD_PROJECT}"
```

[Vertex AI](https://cloud.google.com/vertex-ai?hl=ja) など、関連サービスを有効化し、利用できる状態にします。

```bash
gcloud services enable compute.googleapis.com aiplatform.googleapis.com generativelanguage.googleapis.com run.googleapis.com logging.googleapis.com iap.googleapis.com iamcredentials.googleapis.com cloudresourcemanager.googleapis.com
```

自分がプロジェクトの _オーナー_ または _プロジェクト IAM 管理者_ 相当の権限を持っていることを確認します。

```bash
account=$( gcloud auth list --filter=status:ACTIVE --format='value(account)' )
gcloud projects get-iam-policy "${GOOGLE_CLOUD_PROJECT}" --filter="bindings.members:${account}" | grep -e 'roles/owner' -e 'roles/resourcemanager.projectIamAdmin'
```

## 2. 認証

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

認証情報が生成されたことを確かめましょう。

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

- [L.20](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/01-text-to-text.py#L20) では Multimodal Live API が利用できる `gemini-2.0-flash-lite-001` を指定しています。
- [L.28](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/01-text-to-text.py#L28) の `genai.Client()` は Google の生成 AI クライアントを初期化しています。
- [L.31](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/01-text-to-text.py#L31) `async with` を使用することで、接続の開始と終了が自動的に管理されます。
- [L.44](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/01-text-to-text.py#L44-L47) 非同期的にサーバーからの入力を受け付けます。
- [L.54](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/01-text-to-text.py#L54) `asyncio` パッケージを使うことで効率的に非同期処理を管理します。

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

- [L.61](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/02-text-to-audio.py#L61) 音声での応答を指示します。
- [L.62](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/02-text-to-audio.py#L62-L64) 日本語での応答を "システム指示" として設定しています。このように指定すると、都度プロンプトでお願いする必要がなくなります。
- [L.87](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/01/02-text-to-audio.py#L87) 応答をファイルに書き込みます。

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
