# Gemini Multimodal Live API ハンズオン その 2

## 始めましょう

この手順では Gemini Multimodal Live API に音声を入力し、音声で応答するアプリケーションを確認します。

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="1"></walkthrough-tutorial-difficulty>

**[開始]** ボタンをクリックして次のステップに進みます。

## 1. エディタの起動

[Cloud Shell エディタ](https://cloud.google.com/shell/docs/launching-cloud-shell-editor?hl=ja) を起動していなかった場合、以下のコマンドを実行しましょう。

```bash
cloudshell workspace gemini-multimodal-live-api-handson
```

## 2. Gemini Multimodal Live API の双方向オーディオ通信

Multimodal Live API はリアルタイムの双方向オーディオ通信が行える仕組みをもっています。  
アプリケーションはユーザーのマイクからオーディオ入力をキャプチャして Gemini API に送信、モデルのオーディオ応答を受信してユーザーのスピーカーから再生、という実装が可能です。

![システム アーキテクチャ](https://github.com/heiko-hotz/gemini-multimodal-live-dev-guide/blob/main/assets/audio-client.png?raw=true)

非同期プログラミングによってオーディオの入力と出力を同時に処理し、スムーズで応答性の高いインタラクションを実現するための考慮点を確認してみます。

- マイクからの連続オーディオ ストリームをどのように小さなチャンクに分割し、Gemini API に送信するかはとても重要
- 本サンプルでは while 文で入力ストリームから固定数 (512) ごとのフレーム読み取りを繰り返し実行する実装
- 入力ストリームのサンプル レートを音声認識の一般的な 16 kHz とする場合、各チャンクは 512 フレーム / 16 kHz = 32 ミリ秒のオーディオになる

音声のフォーマットの現在の仕様については [こちら](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-live?hl=ja#audio-formats)、その他の制限については [こちら](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-live?hl=ja#limitations) を参照してください。

## 3. Gemini が音声を解釈するまで

Gemini との会話がどのように実現されるのか、手順をたどってみましょう。

1. **ユーザーが話す**: マイクに向かって話し始めます
2. **オーディオ キャプチャ**: 入力タスクはマイクからオーディオ データを継続的にキャプチャ
3. **チャンキング**: 32 ミリ秒のオーディオがキャプチャされるたび、チャンクが作成されます
4. **API に送信**: この小さなチャンクはすぐ、Gemini API に送信されます
5. **API 処理**: API はチャンクを受信、分析を開始。チャンクは小さく頻繁なので、ユーザーが話している間も、API はオーディオの処理を非常に迅速に開始できます。
6. **モデルの応答**: API がユーザーのターン終了と解釈すると、Gemini はこれまで受信したオーディオに基づいて応答の生成を開始
7. **オーディオ出力**: 応答オーディオはチャンク単位でクライアントに返送。出力タスクはオーディオが到着次第再生を開始、遅延は最小限に抑えられます。

Gemini が賢いポイントは、実はチャンクが `end_of_turn` として送られてきても、すぐにそれを会話の終了とは見做さず、  
音声アクティビティ検出 (VAD) という機能によって**実際のユーザーの発話終了をより正確に表す長い一時停止または無音期間を識別できる**という点です。  
これにより、クライアントサイドの実装上の複雑さも軽減できます。

## 4. サンプル: 音声 → 音声

では実際にサンプルコードを読んでみましょう。  
<walkthrough-editor-open-file filePath="src/02/01-audio-to-audio.py">01-audio-to-audio.py</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/02/01-audio-to-audio.py" startLine="30" endLine="30" startCharacterOffset="4" endCharacterOffset="100">L.31</walkthrough-editor-select-line> pyaudio を使ってオーディオ ハードウェアからの入力ストリームと出力ストリームを管理します
- <walkthrough-editor-select-line filePath="src/02/01-audio-to-audio.py" startLine="50" endLine="50" startCharacterOffset="12" endCharacterOffset="100">L.51</walkthrough-editor-select-line> `asyncio.TaskGroup` を使って、入力・出力を並列タスクとして実行します
- <walkthrough-editor-select-line filePath="src/02/01-audio-to-audio.py" startLine="73" endLine="73" startCharacterOffset="12" endCharacterOffset="100">L.74</walkthrough-editor-select-line> `listen_and_send` ではマイクからの入力を監視し、小さなチャンクを頻繁に Gemini に送信し
- <walkthrough-editor-select-line filePath="src/02/01-audio-to-audio.py" startLine="92" endLine="92" startCharacterOffset="12" endCharacterOffset="100">L.93</walkthrough-editor-select-line> `receive_and_play` では Gemini からの応答を受信し、スピーカーから再生します

## その 2 はこれで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

では続けて、ハンズオン その 3 へ進みましょう！

```bash
teachme 03-low-level-api.md
```
