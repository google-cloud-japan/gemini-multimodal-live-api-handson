# Gemini Multimodal Live API ハンズオン その 4

## 始めましょう

この手順では WebSocket と Web Audio API を使って Gemini Multimodal Live API と対話する、リアルタイムな音声アプリケーションを構築していきます。

そして本パート以降では改めて、企業でも安心して利用できる **Vertex AI 経由での Gemini API** を使っていきます :)

<walkthrough-tutorial-duration duration="20"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="3"></walkthrough-tutorial-difficulty>

**[開始]** ボタンをクリックして次のステップに進みます。

## プロジェクトの設定

この手順の中で実際にリソースを構築する対象のプロジェクトを選択してください。

<walkthrough-project-setup></walkthrough-project-setup>

## 1. エディタの起動

[Cloud Shell エディタ](https://cloud.google.com/shell/docs/launching-cloud-shell-editor?hl=ja) を起動していなかった場合、以下のコマンドを実行しましょう。

```bash
cloudshell workspace gemini-multimodal-live-api-handson
```

## 2. CLI の初期設定

**ハンズオン その 1 を実施された方は読み飛ばしていただいて OK です。**

[gcloud（Google Cloud の CLI ツール)](https://cloud.google.com/sdk/gcloud?hl=ja) のデフォルト プロジェクトを設定します。

```bash
export GOOGLE_CLOUD_PROJECT=<walkthrough-project-id/>
```

```bash
gcloud config set project "${GOOGLE_CLOUD_PROJECT}"
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

## 3. ファイル構成

これまでと異なり、双方向でライブ オーディオ ストリームを処理するため、コードは大幅に複雑になっていきます。  
例えば特徴的な変更点として、話者交代の検知はローカルのフラグを見るのではなく、API 側の機能を使うようになっています。

![システム アーキテクチャ](https://raw.githubusercontent.com/heiko-hotz/gemini-multimodal-live-dev-guide/main/assets/audio-to-audio-websocket.png)

本アプリケーションは次のファイル群で構成されています。

- **01-audio-to-audio.html**: ユーザー インターフェイス。全体的な流れや WebSocket 通信など、コアロジックを含んでいます。
- **audio-recorder.js**: マイクからオーディオをキャプチャし、必要な形式に変換、そののチャンクデータを送信します。
- **audio-recording-worklet.js**: 低レベルのオーディオ処理。float32 から int16 への変換やチャンク化など。
- **audio-streamer.js**: Web Audio API でオーディオを管理。Gemini から受信したチャンクデータのキューイング、バッファリング、再生など、スムーズで継続的な再生を保証します。
- **gemini-live-api.js**: WebSocket を使って Gemini API サーバーと通信し、リアルタイムな音声対話を実現するための機能を集約しています。

音声フォーマットの [現在の仕様](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-live?hl=ja#audio-formats) の通り、Multimodal Live API の入力音声形式は 16 kHz の 16 ビット PCM 形式となっており、その処理は `audio-recording-worklet.js` が担っています。各チャンクには 16 ビット PCM オーディオのサンプルが 2,048 個含まれており、結果として、オーディオ データは約 128 ミリ秒 (2,048 / 16,000 = 0.128 秒) ごとに送信される実装になっています。

## 4. システム構成

Web ブラウザ (JavaScript) から Vertex AI を安全に接続する方法はいくつか考えられますが、今回は多段のプロキシ（中継サーバ）を使う方法を採用します。

- JavaScript と Gemini は直接繋がず、JavaScript からはクラウドに置かれた <walkthrough-editor-open-file filePath="src/proxy/proxy.py">proxy.py</walkthrough-editor-open-file> を経由して Gemini に接続します。
- Gemini への認証・認可は、その Python コードの実行環境に割り当てられた[サービスアカウント](https://cloud.google.com/iam/docs/service-account-overview?hl=ja)で代行します。
- すると今度はこの Python にアクセスできる人は誰でも Gemini を扱えてしまいます。そこで Python の前に [Identity-Aware Proxy (IAP)](https://cloud.google.com/security/products/iap?hl=ja) という認証サービスを挟み、アクセスできる人を制御します。
- すると今度は JavaScript でどのように IAP 認証を通すか困ってしまいそうですが、Python が JavaScript と 同じ場所に置かれているとブラウザが判断すれば、Web サイトにアクセスしたときの認証が Python にも適用され、個別の認証プロセスを省けます。この挙動は[同一オリジンポリシー](https://developer.mozilla.org/ja/docs/Web/Security/Same-origin_policy)と呼ばれる仕様です。
- これを実現するために [Nginx](https://ja.wikipedia.org/wiki/Nginx) というソフトウェアを使って、すべてを [Docker](https://ja.wikipedia.org/wiki/Docker) コンテナにまとめます。

結果として、こんな動きになります。

1. ブラウザでサービスの URL にアクセス
1. IAP でユーザーを認証
1. Nginx が HTML と JavaScript を返す
1. JavaScript が同じ認証情報を使い、Nginx を経由して Python にアクセス
1. Python はブラウザからの要求をそのまま Gemini に転送
1. Python は Gemini の応答をそのままブラウザに返す

## 5. コンテナのビルド

コードを読む前に、まずは動作確認を進めましょう。まずは 4. のシステム構成を実現するため、<walkthrough-editor-open-file filePath="src/Dockerfile">Dockerfile</walkthrough-editor-open-file> を使って、すべてのソースコードをひとつのコンテナにまとめます。

```bash
sed -e "s|<YOUR_PROJECT_ID>|${GOOGLE_CLOUD_PROJECT}|g" src/04/01-audio-to-audio.html > src/04/index.html
docker build -t app-0401 --build-arg SRC_DIR=04/ src
```

それを起動します。

```bash
docker rm -f app-0401 > /dev/null 2>&1
docker run --rm --name app-0401 -p 8080:8080 -e GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT} -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/creds.json -v ${GOOGLE_APPLICATION_CREDENTIALS}:/tmp/creds.json app-0401
```

Web preview ボタンを押し、"ポート 8080 でプレビュー" を選びましょう。  
<walkthrough-web-preview-icon></walkthrough-web-preview-icon>

マイクボタンをクリックして、何か話しかけてみてください！

確認ができたら `Ctrl + C` を何度か押してプロセスを終了させましょう。

## 6. Cloud Run へのデプロイ

ではこれを、世界に向けてクラウド上に展開してみます。

まず、コンテナを保存するレジストリを [Artifact Registry](https://cloud.google.com/artifact-registry?hl=ja) というサービスの中に作ります。

```bash
gcloud artifacts repositories create genai --repository-format docker --location asia-northeast1 --description "Docker repository for GenAI hands-on"
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
docker tag app-0401 asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0401
docker push asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0401
```

そして Cloud Run サービスを作成しましょう。

```bash
gcloud beta run deploy genai-app-04 --image asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0401 --region asia-northeast1 --platform managed --no-allow-unauthenticated --iap --quiet
```

自分自身にアクセス許可を与えます。

```bash
gcloud beta iap web add-iam-policy-binding --member "user:$(gcloud config get-value core/account)" --role "roles/iap.httpsResourceAccessor" --resource-type "cloud-run" --service genai-app-04 --region asia-northeast1
```

サービスがデプロイされたら、以下のコマンドで返ってくる URL にアクセスしてみてください。

```bash
gcloud run services describe genai-app-04 --region asia-northeast1 --format='value(status.address.url)'
```

## 7. ログの確認

Cloud Run で出力されたログをクラウド上のコンソールから確認してみましょう。

1. [Cloud Run](https://console.cloud.google.com/run) にアクセスし
1. `genai-app-04` というサービス名をクリックし、[ログ](https://console.cloud.google.com/run/detail/asia-northeast1/genai-app-04/logs) というタブをクリックしましょう。

ログは確認できましたか？

クラウドの画面でもサービスの状況が確認できたので、いよいよコードで実装をみていきましょう。  
改めて<walkthrough-spotlight-pointer spotlightId="cloud-shell-maximize-button" target="cloudshell">Editor を最大化</walkthrough-spotlight-pointer>します。

## 8. リアルタイム音声チャットのコード確認

コードで確認してみます。  
<walkthrough-editor-open-file filePath="src/04/01-audio-to-audio.html">01-audio-to-audio.html</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/04/01-audio-to-audio.html" startLine="33" endLine="33" startCharacterOffset="4" endCharacterOffset="100">L.34</walkthrough-editor-select-line> コードが複雑になってきたため、役割ごとにファイルを分割しています。
- <walkthrough-editor-select-line filePath="src/04/01-audio-to-audio.html" startLine="53" endLine="53" startCharacterOffset="10" endCharacterOffset="150">L.54</walkthrough-editor-select-line> Vertex AI で利用するモデルは完全なパス形式で指定します。
- <walkthrough-editor-select-line filePath="src/04/01-audio-to-audio.html" startLine="128" endLine="130" startCharacterOffset="10" endCharacterOffset="100">L.129</walkthrough-editor-select-line> チャンクとなったオーディオデータは都度、Gemini API サーバーに送信されます。

ご興味があれば <walkthrough-editor-open-file filePath="src/shared/audio-recorder.js">audio-recorder.js</walkthrough-editor-open-file> や <walkthrough-editor-open-file filePath="src/shared/audio-streamer.js">audio-streamer.js</walkthrough-editor-open-file>、<walkthrough-editor-open-file filePath="src/shared/gemini-live-api.js">gemini-live-api.js</walkthrough-editor-open-file> の実装もぜひご覧ください。

## 9. サービスの削除

Cloud Run サービスを削除しましょう。

```bash
gcloud run services delete genai-app-04 --region asia-northeast1 --quiet
```

## その 4 はこれで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

では続けて、ハンズオン その 5 へ進みましょう！

```bash
teachme tutorials/05-video-and-audio.md
```
