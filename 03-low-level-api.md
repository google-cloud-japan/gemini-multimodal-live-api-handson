# Gemini Multimodal Live API ハンズオン その 3

## 始めましょう

この手順ではブラウザの組み込み WebSocket API を使い、かつ "Gemini API と直接通信する低レイヤーでの実装" を試します。

ただしこのパートでは、API を直接呼び出す都合上、企業向けではない、一般開発者向けのエンドポイントを利用する実装になっています。**企業での利用は推奨されません**のでご注意ください。

<walkthrough-tutorial-duration duration="15"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="1"></walkthrough-tutorial-difficulty>

**[開始]** ボタンをクリックして次のステップに進みます。

## 1. エディタの起動

[Cloud Shell エディタ](https://cloud.google.com/shell/docs/launching-cloud-shell-editor?hl=ja) を起動していなかった場合、以下のコマンドを実行しましょう。

```bash
cloudshell workspace gemini-multimodal-live-api-handson
```

## 2. サンプル: テキスト → テキスト

これまで Python でやってきたことを、ブラウザ (JavaScript) で実施する例をみてみます。

まずは入力も JavaScript にハードコーディングしてある小さなサンプルコードで確認してみます。  
<walkthrough-editor-open-file filePath="src/03/01-text-to-text.html">01-text-to-text.html</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/03/01-text-to-text.html" startLine="38" endLine="38" startCharacterOffset="6" endCharacterOffset="200">L.39</walkthrough-editor-select-line> Gemini の双方向 WebSocket API エンドポイントですが、一般開発者向けです。ご注意ください。
- <walkthrough-editor-select-line filePath="src/03/01-text-to-text.html" startLine="41" endLine="41" startCharacterOffset="6" endCharacterOffset="100">L.42</walkthrough-editor-select-line> WebSocket オブジェクトを作成します。
- <walkthrough-editor-select-line filePath="src/03/01-text-to-text.html" startLine="46" endLine="57" startCharacterOffset="8" endCharacterOffset="100">L.47</walkthrough-editor-select-line> Gemini API は、 WebSocket 接続が確立された後、最初にセットアップ メッセージを送信する必要があります。
- <walkthrough-editor-select-line filePath="src/03/01-text-to-text.html" startLine="70" endLine="70" startCharacterOffset="10" endCharacterOffset="100">L.71</walkthrough-editor-select-line> `setupComplete` はユーザーがコンテンツを送信し始められることを示しています。

## 3. テキスト → テキスト Web アプリの実行

[Google Cloud の認証情報](https://console.cloud.google.com/apis/credentials)で管理できる API キーを発行します。  
ただし API キーは商用利用においては推奨されない方法です。ハンズオンの最後の手順にあるキーの削除は必ず実行してください。

```bash
gcloud services api-keys create --key-id "gemini-api-$(whoami | grep -oE '[[:alpha:]]+')" --display-name "A key for the Gemini Multimodal Live API hands-on" --api-target "service=generativelanguage.googleapis.com"
```

この応答に含まれる `keyString` が **以降のステップで利用する API キー** です。

<walkthrough-editor-select-line filePath="src/03/01-text-to-text.html" startLine="37" endLine="37" startCharacterOffset="22" endCharacterOffset="36">L.38</walkthrough-editor-select-line> `<YOUR_API_KEY>` を API キーと置き換え、Web サーバーを起動します。

```bash
python src/server.py
```

Web preview ボタンを押し、"ポート 8080 でプレビュー" を選んでみましょう。  
<walkthrough-web-preview-icon></walkthrough-web-preview-icon>

`03` > `01-text-to-text.html` を選択し、デモ画面を開いてみましょう。  
ハードコードされた内容に対する会話ですが、動作したでしょうか？

## 4. サンプル: テキスト → 音声

次は入力欄にテキストを入力し、それを Gemini モデルに送信、ブラウザーで音声が再生されるサンプルです。

JavaScript を読んでみましょう。  
<walkthrough-editor-open-file filePath="src/03/02-text-to-audio.html">02-text-to-audio.html</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/03/02-text-to-audio.html" startLine="69" endLine="69" startCharacterOffset="10" endCharacterOffset="100">L.70</walkthrough-editor-select-line> 音声の再生のために [AudioContext](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API#web_audio_api_interfaces) を利用します。
- <walkthrough-editor-select-line filePath="src/03/02-text-to-audio.html" startLine="92" endLine="92" startCharacterOffset="6" endCharacterOffset="100">L.93</walkthrough-editor-select-line> 音声の再生そのものは `processAudioQueue` 関数で管理されています。
- <walkthrough-editor-select-line filePath="src/03/02-text-to-audio.html" startLine="224" endLine="224" startCharacterOffset="14" endCharacterOffset="100">L.225</walkthrough-editor-select-line> 再生対象である Gemini から受け取る音声データはここでキューに追加されます。

## 5. テキスト → 音声 Web アプリの実行

さきほどと同様、  
<walkthrough-editor-select-line filePath="src/03/02-text-to-audio.html" startLine="58" endLine="58" startCharacterOffset="22" endCharacterOffset="36">L.59</walkthrough-editor-select-line> `<YOUR_API_KEY>` を API キーと置き換えましょう。

もしプレビューを閉じてしまっていたら、改めて Web preview ボタンを押し、"ポート 8080 でプレビュー" を選び  
<walkthrough-web-preview-icon></walkthrough-web-preview-icon>

`03` > `02-text-to-audio.html` を選択、デモ画面を開いてみましょう。  
自由にコメントを入力してみてください。Gemini が音声で応えてくれます！

## その 3 はこれで終わりです

もしまだサーバーが起動していたら `Ctrl + C` で停止してください。

また、以下のコマンドを実行し、一時的に発行した API キーを削除しましょう。

```bash
gcloud services api-keys delete "gemini-api-$(whoami | grep -oE '[[:alpha:]]+')"
```

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

では続けて、ハンズオン その 4 へ進みましょう！

```bash
teachme 04-vertex-ai.md
```
