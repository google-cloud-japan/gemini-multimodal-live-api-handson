# Gemini Multimodal Live API ハンズオン その 5

## 始めましょう

その 4 ではリアルタイムで音声で会話するデモでした。次はみなさんの **Web カメラ、もしくは画面を共有しながら** Gemini に話しかけてみましょう！

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="2"></walkthrough-tutorial-difficulty>

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
gcloud run deploy genai-app-0501 --image asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0501 --region asia-northeast1 --platform managed --allow-unauthenticated --quiet
```

サービスがデプロイされたら、以下のコマンドで帰ってきた URL にアクセスしてみてください。

```bash
gcloud run services describe genai-app-0501 --region asia-northeast1 --format='value(status.address.url)'
```

ブラウザからでも Gemini のマルチモーダルでリアルタイムな機能は確認できたでしょうか？

## 5. サービスの削除

みなさんがデプロイした Cloud Run サービスは現在、世界中からアクセスできる状態です。念のためサービスを削除しましょう。

```bash
gcloud run services delete genai-app-0501 --region asia-northeast1 --quiet
```

## その 5 はこれで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

これですべてのハンズオン体験は終了です。

お疲れさまでした！
