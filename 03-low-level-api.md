# Gemini Multimodal Live API ハンズオン その 3

## 始めましょう

この手順ではブラウザの組み込み WebSocket API を使い、かつ "Gemini API と直接通信する低レイヤーでの実装" を試します。

ただしこのパートでは、API を直接呼び出す都合上、企業向けではない、一般開発者向けのエンドポイントを利用する実装になっています。**企業での利用は推奨されません**のでご注意ください。

## 1. サンプル: テキスト → テキスト

これまで Python でやってきたことを、ブラウザ (JavaScript) で実施する例をみてみます。

まずは入力も JavaScript にハードコーディングしてある小さなサンプルコードで確認してみます。

- [L.39](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/01-text-to-text.html#L39) Gemini の双方向 WebSocket API エンドポイントですが、一般開発者向けです。ご注意ください。
- [L.42](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/01-text-to-text.html#L42) WebSocket オブジェクトを作成します。
- [L.47](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/01-text-to-text.html#L47-L58) Gemini API は、 WebSocket 接続が確立された後、最初にセットアップ メッセージを送信する必要があります。
- [L.71](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/01-text-to-text.html#L71) `setupComplete` はユーザーがコンテンツを送信し始められることを示しています。

## 2. テキスト → テキスト Web アプリの実行

[Google Cloud の認証情報](https://console.cloud.google.com/apis/credentials)で管理できる API キーを発行します。  
ただし API キーは商用利用においては推奨されない方法です。ハンズオンの最後の手順にあるキーの削除は必ず実行してください。

```bash
gcloud services api-keys create --key-id "gemini-api-$(whoami | grep -oE '[[:alpha:]]+')" --display-name "A key for the Gemini Multimodal Live API hands-on" --api-target "service=generativelanguage.googleapis.com"
```

この応答に含まれる `keyString` が **以降のステップで利用する API キー** です。

- [L.38](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/01-text-to-text.html#L38) `<YOUR_API_KEY>` を API キーと置き換え、Web サーバーを起動します。

```bash
python src/server.py
```

ブラウザで http://localhost:8080 を開きましょう。

`03` > `01-text-to-text.html` を選択し、デモ画面を開いてみましょう。  
ハードコードされた内容に対する会話ですが、動作したでしょうか？

## 3. サンプル: テキスト → 音声

次は入力欄にテキストを入力し、それを Gemini モデルに送信、ブラウザーで音声が再生されるサンプルです。

- [L.70](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/02-text-to-audio.html#L70) 音声の再生のために [AudioContext](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API#web_audio_api_interfaces) を利用します。
- [L.93](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/02-text-to-audio.html#L93) 音声の再生そのものは `processAudioQueue` 関数で管理されています。
- [L.225](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/02-text-to-audio.html#L225) 再生対象である Gemini から受け取る音声データはここでキューに追加されます。

## 4. テキスト → 音声 Web アプリの実行

さきほどと同様、[L.59](https://github.com/google-cloud-japan/gemini-multimodal-live-api-handson/blob/main/src/03/02-text-to-audio.html#L59) の `<YOUR_API_KEY>` を API キーと置き換えましょう。

ブラウザで http://localhost:8080 を開き、  
`03` > `02-text-to-audio.html` を選択、デモ画面を開いてみましょう。  
自由にコメントを入力してみてください。Gemini が音声で応えてくれます！

## これで終わりです

もしまだサーバーが起動していたら `Ctrl + C` で停止してください。

また、以下のコマンドを実行し、一時的に発行した API キーを削除しましょう。

```bash
gcloud services api-keys delete "gemini-api-$(whoami | grep -oE '[[:alpha:]]+')"
```
