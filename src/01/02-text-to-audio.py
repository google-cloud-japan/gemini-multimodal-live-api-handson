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
import contextlib
import wave
from google import genai
from google.genai import types


# Gemini モデルの指定
MODEL_ID = "gemini-2.0-flash-001"

# Gemini 使用音声の指定（Puck, Charon, Kore, Fenrir, Aoede から選択）
VOICE_NAME = "Aoede"


@contextlib.contextmanager
def wave_file(filename, channels=1, rate=24000, sample_width=2):
    """
    WAVE 形式の音声ファイルを保存します

    Args:
        filename (str): 音声ファイルのファイル名
        channels (int): 音声ファイルのチャンネル数（デフォルトは 1: モノラル）
        rate (int): 音声ファイルのサンプルレート（デフォルトは 24000 Hz）
        sample_width (int): 音声ファイルのサンプル幅（デフォルトは 2 バイト）

    Yields:
        wave.Wave_write: WAVE ファイルオブジェクト
    """
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        yield wf


async def main():
    """
    Gemini Multimodal Live API に対して音声ベースで一度だけやりとりする非同期関数です
    """
    # 生成 AI クライアントの初期化
    client = genai.Client()

    # Gemini モデルとのライブ接続を確立
    async with client.aio.live.connect(
        model=MODEL_ID,
        config=types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],  # 応答として音声を受け取ることを指定
            system_instruction=types.Content(parts=[
                types.Part(text="Could you respond in Japanese?")
            ]),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NAME),
                ),
            ),
        ),
    ) as session:
        # 音声データを書き込むための WAVE ファイルを作成
        with wave_file("audio.wav") as wav:
            message = "こんには Gemini!"
            print("> ", message, "\n")
            await session.send(input=message, end_of_turn=True)

            first = True

            # ライブセッションから非同期に応答を受信
            async for response in session.receive():
                if response.data is not None:
                    model_turn = response.server_content.model_turn
                    if first:
                        print(model_turn.parts[0].inline_data.mime_type)
                    first = False
                    wav.writeframes(response.data)  # 受信した音声データを WAVE ファイルに書き込む

        print("音声ファイルを保存しました")


if __name__ == "__main__":
    asyncio.run(main())
