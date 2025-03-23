# Gemini Multimodal Live API ハンズオン その 5

## 始めましょう

その 4 ではリアルタイムで音声で会話するデモでした。次はみなさんの **Web カメラ、もしくは画面を共有しながら** Gemini に話しかけてみましょう！

<walkthrough-tutorial-duration duration="15"></walkthrough-tutorial-duration>
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

**ハンズオン その 1 または 4 を実施された方は読み飛ばし、次へお進みください！**

gcloud（[Google Cloud の CLI ツール](https://cloud.google.com/sdk/gcloud?hl=ja) のデフォルト プロジェクトを設定します。

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

## 3. コンテナのビルド

その 4 同様、まずは動作確認をしてみます。資材をコンテナとしてビルドし、

```bash
sed -e "s|<YOUR_PROJECT_ID>|${GOOGLE_CLOUD_PROJECT}|g" src/05/01-video-and-audio.html > src/05/index.html
docker build -t app-0501 --build-arg SRC_DIR=05/ src
```

それを手元の環境で起動してみます。

```bash
docker rm -f app-0401 app-0501 > /dev/null 2>&1
docker run --rm --name app-0501 -p 8080:8080 -e GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT} -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/creds.json -v ${GOOGLE_APPLICATION_CREDENTIALS}:/tmp/creds.json app-0501
```

Web preview ボタンを押し、"ポート 8080 でプレビュー" を選びましょう。  
<walkthrough-web-preview-icon></walkthrough-web-preview-icon>

マイクボタンをクリックする前に、**カメラボタンか画面共有ボタンを押して、動画をアプリケーションに読み込ませます。**  
その上でマイクボタンを押し、Gemini に何か話しかけてみてください！

どうでしょう？Gemini は状況を理解してくれましたか？

確認ができたら `Ctrl + C` を何度か押してプロセスを終了させましょう。

## 4. Cloud Run へのデプロイ

今回も認証なしのエンドポイントとして Cloud Run にサービスをデプロイしてみます。コンテナを保存するレジストリを作り、さきほどビルドしたコンテナイメージを push します。

```bash
docker tag app-0501 asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0501
docker push asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0501
```

そして Cloud Run サービスを作成しましょう。

```bash
gcloud run deploy genai-app-05 --image asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0501 --region asia-northeast1 --platform managed --allow-unauthenticated --quiet
```

サービスがデプロイされたら、以下のコマンドで帰ってきた URL にアクセスしてみてください。

```bash
gcloud run services describe genai-app-05 --region asia-northeast1 --format='value(status.address.url)'
```

ブラウザからでも Gemini のマルチモーダルでリアルタイムな機能は確認できたでしょうか？

## 5. リアルタイム動画 × 音声チャットのコード確認

コードで確認してみます。  
<walkthrough-editor-open-file filePath="src/05/01-video-and-audio.html">01-video-and-audio.html</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/05/01-video-and-audio.html" startLine="45" endLine="45" startCharacterOffset="6" endCharacterOffset="100">L.46</walkthrough-editor-select-line> Web カメラやスクリーンの共有は <walkthrough-editor-open-file filePath="src/shared/media-handler.js">media-handler.js</walkthrough-editor-open-file> で管理しています。
- <walkthrough-editor-select-line filePath="src/05/01-video-and-audio.html" startLine="248" endLine="248" startCharacterOffset="12" endCharacterOffset="150">L.249</walkthrough-editor-select-line> Web カメラの動画を 500 ミリ秒おきに画像として切り出し、Gemini に WebSocket 経由で送信しています。
- <walkthrough-editor-select-line filePath="src/05/01-video-and-audio.html" startLine="280" endLine="280" startCharacterOffset="12" endCharacterOffset="150">L.281</walkthrough-editor-select-line> スクリーン共有も Web カメラ同様、500 ミリ秒単位で Gemini に画像を転送しているのがわかります。

## 6. 関数呼び出し

関数呼び出しのコードをコンテナとしてビルドし、

```bash
sed -e "s|<YOUR_PROJECT_ID>|${GOOGLE_CLOUD_PROJECT}|g" src/05/02-function-calling.html > src/05/index.html
docker build -t app-0502 --build-arg SRC_DIR=05/ src
```

それを手元の環境で起動してみます。

```bash
docker rm -f app-0401 app-0501 app-0502 > /dev/null 2>&1
docker run --rm --name app-0502 -p 8080:8080 -e GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT} -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/creds.json -v ${GOOGLE_APPLICATION_CREDENTIALS}:/tmp/creds.json app-0502
```

Web preview ボタンを押し、"ポート 8080 でプレビュー" を選びましょう。  
<walkthrough-web-preview-icon></walkthrough-web-preview-icon>

マイクボタンをクリックして **「Gemini Robotics って知っている？」** と聞いてみてください。  
[Gemini Robotics](https://blog.google/intl/ja-jp/company-news/technology/gemini-robotics-ai/) は Google DeepMind の最新の研究に基づくものであり、**LLM 単体では知り得ない状況にも正確に対応できている**ことがわかります。

確認ができたら `Ctrl + C` を何度か押してプロセスを終了させましょう。

## 7. Cloud Run へ関数呼び出し版をデプロイ

アプリケーションをビルドして、コンテナイメージを push します。

```bash
docker tag app-0502 asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0502
docker push asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0502
```

既存の Cloud Run サービスを、**関数呼び出し版に更新**してみます。

```bash
gcloud run deploy genai-app-05 --image asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0502 --region asia-northeast1 --quiet
```

制御が返ってきたら、以下のコマンドで帰ってきた URL にアクセスしてみてください。先ほどと同じ URL ですが、最新情報にも応えられるようになっているはずです。

```bash
gcloud run services describe genai-app-05 --region asia-northeast1 --format='value(status.address.url)'
```

Cloud Run には[リビジョン](https://console.cloud.google.com/run/detail/asia-northeast1/genai-app-05/revisions) という概念があり、デプロイ履歴をもどしたりすることもできます。

## 8. 関数呼び出しのコード確認

Editor が小さくなっていたら <walkthrough-spotlight-pointer spotlightId="cloud-shell-maximize-button" target="cloudshell">最大化</walkthrough-spotlight-pointer>して、コードを確認しましょう。
<walkthrough-editor-open-file filePath="src/05/02-function-calling.html">02-function-calling.html</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/05/02-function-calling.html" startLine="67" endLine="67" startCharacterOffset="22" endCharacterOffset="400">L.68</walkthrough-editor-select-line> これまでシステム指示は「日本語で応答せよ」だけでしたが、今回は検索が必要な場合は Google 検索を行うように追加で指示しています。
- <walkthrough-editor-select-line filePath="src/05/02-function-calling.html" startLine="71" endLine="71" startCharacterOffset="10" endCharacterOffset="100">L.72</walkthrough-editor-select-line> ツールとして「Google 検索」を有効化しています。任意の API を呼び出すような実装も可能です。

## 9. サービスの削除

前回同様、デプロイした Cloud Run サービスは現在、世界中からアクセスできる状態です。念のためサービスを削除しましょう。

```bash
gcloud run services delete genai-app-05 --region asia-northeast1 --quiet
```

## その 5 はこれで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

これですべてのハンズオン体験は終了です。

お疲れさまでした！
