# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import traceback
import pyaudio
from google import genai

# Gemini モデルの指定
MODEL_ID = "gemini-2.0-flash-001"

# Gemini 使用音声の指定（Puck, Charon, Kore, Fenrir, Aoede から選択）
VOICE_NAME = "Fenrir"


async def audio_loop():
    model_speaking = False  # Gemini が発話中かどうかを示すフラグ
    session = None  # Gemini Live API セッション

    pya = pyaudio.PyAudio()
    mic_info = pya.get_default_input_device_info()  # デフォルトのマイクの情報を取得

    try:
        # 生成 AI クライアントの初期化
        client = genai.Client()

        # Gemini モデルとのライブ接続を確立
        async with (
            client.aio.live.connect(
                model=MODEL_ID,
                config=types.LiveConnectConfig(
                    response_modalities=[types.Modality.AUDIO],  # 応答として音声を受け取ることを指定
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NAME),
                        ),
                    ),
                ),
            ) as session,
            asyncio.TaskGroup() as tg,
        ):
            print("Connected to Gemini.")

            # マイク入力ストリームを開く
            input_stream = await asyncio.to_thread(
                pya.open,
                format=pyaudio.paInt16,  # 16bit PCM
                channels=1,  # モノラル
                rate=16000,  # サンプリングレート 16kHz
                input=True,  # 入力
                input_device_index=mic_info["index"],  # デフォルトのマイクを使用
                frames_per_buffer=512,  # バッファサイズ 512 フレーム
            )
            # スピーカー出力ストリームを開く
            output_stream = await asyncio.to_thread(
                pya.open,
                format=pyaudio.paInt16,  # 16bit PCM
                channels=1,  # モノラル
                rate=24000,  # サンプリングレート 24kHz
                output=True,  # 出力モード
            )

            async def listen_and_send():
                """
                マイクからの入力を監視し、Gemini に送信するタスク
                """
                nonlocal model_speaking
                while True:
                    if not model_speaking:
                        try:
                            # マイクから音声データをノンブロッキングで読み取り
                            data = await asyncio.to_thread(input_stream.read, 512, exception_on_overflow=False)
                            # そのデータを Gemini に送信
                            await session.send(input={"data": data, "mime_type": "audio/pcm"}, end_of_turn=True)
                        except OSError as e:
                            print(f"Audio input error: {e}")
                            await asyncio.sleep(0.1)
                    else:
                        # Gemini 発話中は待機
                        await asyncio.sleep(0.1)

            async def receive_and_play():
                """
                Gemini からの音声応答を受信し、スピーカーから再生するタスク
                """
                nonlocal model_speaking
                while True:
                    # Gemini からの応答を受信
                    async for response in session.receive():
                        server_content = response.server_content  # 応答のコンテンツを取得
                        if server_content and server_content.model_turn:  # モデルのターンがある場合
                            model_speaking = True
                            for part in server_content.model_turn.parts:
                                if part.inline_data:
                                    # 音声データをノンブロッキングでスピーカーに出力
                                    await asyncio.to_thread(output_stream.write, part.inline_data.data)

                        if server_content and server_content.turn_complete:  # ターンの完了が通知された場合
                            print("Turn complete")
                            model_speaking = False

            # listen_and_send と receive_and_play を並行して実行
            tg.create_task(listen_and_send())
            tg.create_task(receive_and_play())

        print("Connection to Gemini closed.")

    except Exception as e:
        traceback.print_exception(None, e, e.__traceback__)


if __name__ == "__main__":
    asyncio.run(audio_loop(), debug=True)
