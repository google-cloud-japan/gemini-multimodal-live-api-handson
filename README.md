# Gemini Multimodal Live API ハンズオン

このリポジトリは、Google の [Gemini Multimodal Live API](https://developers.googleblog.com/ja/gemini-2-0-level-up-your-apps-with-real-time-multimodal-interactions/) をサンプル アプリケーションを通して体験するためのガイドです。ハンズオンを通し、見て、聴いて、人間と自然にやりとりできる Gemini の能力を活かしたリアルタイム アプリケーションを作ってみましょう！

## 作りながら学ぶ重要概念

- **リアルタイム コミュニケーション**

  - WebSocket ベース ストリーミング処理
  - 双方向のオーディオ チャット
  - リアルタイムビデオ処理
  - 話者交代と割り込み処理

- **オーディオ**

  - マイク入力キャプチャ
  - オーディオのチャンク化とストリーミング
  - 音声アクティビティ検出 (VAD)
  - リアルタイム オーディオ再生

- **ビデオ**

  - ウェブカメラとスクリーンのキャプチャ
  - フレーム処理とエンコード
  - オーディオとビデオの同時ストリーミング
  - 効率的なメディア処理

- **商用機能**

  - System instructions
  - クラウドへのデプロイ
  - エンタープライズ セキュリティ

## ハンズオン

### 資材をダウンロード

Google Cloud のコンソールを開き、[Cloud Shell](https://cloud.google.com/shell/docs/launching-cloud-shell?hl=ja) を起動してください。  
Cloud Shell が起動したら、**ルートディレクトリ直下に** GitHub からリポジトリをクローンしましょう。

```sh
git clone https://github.com/pottava/gemini-multimodal-live-demo.git
```

### 1. Gemini Multimodal Live API の基本

まずはテキストを入力にして、テキストまたはオーディオを出力とするサンプルコードを追いかけ、動かしてみましょう。

1. テキスト → テキスト
2. テキスト → 音声

```sh
teachme gemini-multimodal-live-demo/01-text-and-audio.md
```

### 2. Python での 音声 → 音声 アプリ実装例

マイクが使えるローカル環境ならともかく、クラウド環境上 Python だけで `音声 → 音声` の生成 AI アプリは動かせません。  
とはいえ、基本的な挙動を確認するにはコードでの確認は有意義です。一緒に読んでみましょう。

```sh
teachme gemini-multimodal-live-demo/02-audio-to-audio.md
```

### 3. 低レイヤ API を使った Web アプリの基本

JavaScript を使い、ブラウザでのシンプルな `テキスト → テキスト` & `テキスト → 音声` アプリケーションを作ってみましょう。

```sh
teachme gemini-multimodal-live-demo/03-low-level-api.md
```

### 4. Vertex API 企業向け生成 AI アプリ

リアルタイム音声チャットを Vertex AI 経由で実現して、Cloud Run にデプロイしてみましょう。

```sh
teachme gemini-multimodal-live-demo/04-vertex-ai.md
```

### 5. Multimodal 生成 AI アプリ

ビデオ + 音声を入力として、Gemini から音声で回答をもらうアプリケーションを実装してみます。

```sh
teachme gemini-multimodal-live-demo/05-video-and-audio.md
```
