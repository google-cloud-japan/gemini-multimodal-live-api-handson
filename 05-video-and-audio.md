# Gemini Multimodal Live API ハンズオン その 5

## 始めましょう

その 4 ではリアルタイムで音声で会話するデモでした。次はみなさんの **Web カメラ、もしくは画面を共有しながら** Gemini に話しかけてみましょう！

## 1. CLI の初期設定

**ハンズオン その 1 または 4 を実施された方は読み飛ばし、次へお進みください！**

gcloud（Google Cloud の CLI ツール) を[こちらの方法でインストール](https://cloud.google.com/sdk/docs/install-sdk?hl=ja) し、以下のコマンドにあなたの **プロジェクト ID** を指定し、実行してください。

```bash
export GOOGLE_CLOUD_PROJECT=
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

## 2. コンテナのビルド

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

ブラウザで http://localhost:8080 を開きましょう。

マイクボタンをクリックする前に、**カメラボタンか画面共有ボタンを押して、動画をアプリケーションに読み込ませます。**  
その上でマイクボタンを押し、Gemini に何か話しかけてみてください！

どうでしょう？Gemini は状況を理解してくれましたか？

確認ができたら `Ctrl + C` を何度か押してプロセスを終了させましょう。

## 3. Cloud Run へのデプロイ

今回も認証なしのエンドポイントとして Cloud Run にサービスをデプロイしてみます。コンテナを保存するレジストリを作り、さきほどビルドしたコンテナイメージを push します。

```bash
docker tag app-0501 asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0501
docker push asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0501
```

そして Cloud Run サービスを作成しましょう。

```bash
gcloud beta run deploy genai-app-05 --image asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0501 --region asia-northeast1 --platform managed --no-allow-unauthenticated --iap --quiet
```

自分自身にアクセス許可を与えます。

```bash
account=$( gcloud config get-value core/account )
gcloud beta iap web add-iam-policy-binding --member "user:${account}" --role "roles/iap.httpsResourceAccessor" --resource-type "cloud-run" --service genai-app-05 --region asia-northeast1
```

サービスがデプロイされたら、以下のコマンドで帰ってきた URL にアクセスしてみてください。

```bash
gcloud run services describe genai-app-05 --region asia-northeast1 --format='value(status.address.url)'
```

ブラウザからでも Gemini のマルチモーダルでリアルタイムな機能は確認できたでしょうか？

## 4. リアルタイム動画 × 音声チャットのコード確認

コードで確認してみます。

- [L.46](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/05/01-video-and-audio.html#L46) Web カメラやスクリーンの共有は [media-handler.js](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/shared/media-handler.js) で管理しています。
- [L.249](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/05/01-video-and-audio.html#L249-L263) Web カメラの動画を [500 ミリ秒おき](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/shared/media-handler.js#L125) に画像として切り出し、Gemini に WebSocket 経由で送信しています。つまりこの実装は 2 fps です。
- [L.281](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/05/01-video-and-audio.html#L281-L295) スクリーン共有も Web カメラ同様、500 ミリ秒単位で Gemini に画像を転送しているのがわかります。

## 5. 関数呼び出し

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

ブラウザで http://localhost:8080 を開き

マイクボタンをクリックして **「Gemini Robotics って知っている？」** と聞いてみてください。  
[Gemini Robotics](https://blog.google/intl/ja-jp/company-news/technology/gemini-robotics-ai/) は Google DeepMind の最新の研究に基づくものであり、**LLM 単体では知り得ない状況にも正確に対応できている**ことがわかります。

確認ができたら `Ctrl + C` を何度か押してプロセスを終了させましょう。

## 6. Cloud Run へ関数呼び出し版をデプロイ

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

## 7. 関数呼び出しのコード確認

- [L.68](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/05/02-function-calling.html#L68) これまでシステム指示は「日本語で応答せよ」だけでしたが、今回は検索が必要な場合は Google 検索を行うように追加で指示しています。
- [L.72](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/05/02-function-calling.html#L72) ツールとして「Google 検索」を有効化しています。任意の API を呼び出すような実装も可能です。

## 8. サービスの削除

デプロイした Cloud Run サービスを削除しましょう。

```bash
gcloud run services delete genai-app-05 --region asia-northeast1 --quiet
```
