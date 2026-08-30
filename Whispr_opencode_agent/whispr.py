import sys
# json is important for translating output data from this python code to other coding languages
import json
import os

WHISPER_URL = "http://100.X.X.X:8085/transcribe"
GEMMA_URL = "http://100.X.X.X:8084"

def process_voice(audio_path: str) -> str:

    try:
        import requests
    except ImportError:
        return json.dumps({
            "error": "Missing requests dependency."
        })

    if not os.path.exists(audio_path):
        return json.dumps({
            "error": f"Audio file not found: {audio_path}"
        })

    try:

        # -------------------------
        # 1. Send audio to Whisper
        # -------------------------

        with open(audio_path, "rb") as audio:

            whisper_response = requests.post(
                WHISPER_URL,
                files={
                    "audio": (
                        os.path.basename(audio_path),
                        audio
                    )
                },
                timeout=3000
            )

        if whisper_response.status_code != 200:
            return json.dumps({
                "success": False,
                "error": (
                    f"Whisper server returned "
                    f"{whisper_response.status_code}: "
                    f"{whisper_response.text}"
                )
            })

        whisper_data = whisper_response.json()

        if not whisper_data.get("success"):
            return json.dumps({
                "success": False,
                "error": whisper_data.get(
                    "error",
                    "Whisper transcription failed"
                )
            })

        user_text = whisper_data["text"].strip()

        if not user_text:
            return json.dumps({
                "success": False,
                "error": "Whisper returned empty transcription"
            })

        # -------------------------
        # 2. Send text to Gemma
        # -------------------------

        endpoint = f"{GEMMA_URL}/v1/chat/completions"

        payload = {
            "model": "studio-gemma4-optiq-q4//Users/Shared/models/mlx/gemma-4-31B-it-qat-OptiQ-4bit",
            "messages": [
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            "temperature": 0.3,
            "top_p": 0.3
        }

        gemma_response = requests.post(
            endpoint,
            json=payload,
            timeout=1800
        )

        if gemma_response.status_code != 200:
            return json.dumps({
                "success": False,
                "transcription": user_text,
                "error": (
                    f"Gemma server returned "
                    f"{gemma_response.status_code}: "
                    f"{gemma_response.text}"
                )
            })

        gemma_data = gemma_response.json()

        gemma_output = (
            gemma_data["choices"][0]["message"]["content"]
        )

        return json.dumps({
            "success": True,
            "user_prompt": user_text,
            "gemma_output": gemma_output
        })

    except Exception as e:

        return json.dumps({
            "success": False,
            "error": f"Pipeline failure: {str(e)}"
        })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python whispr.py <audio_path>"
        }))
        sys.exit(1)
    print(process_voice(sys.argv[1]))
