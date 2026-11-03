from fastapi import FastAPI, UploadFile, File

from mlx_audio.stt.utils import load_model

import tempfile
import os

app = FastAPI()

WHISPER_MODEL = "/Users/Shared/models/mlx/whisper-large-v3-turbo-4bit"

model = load_model(WHISPER_MODEL)

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):

    suffix = os.path.splitext(audio.filename or "")[1] or ".wav"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:
        audio_data = await audio.read()
        temp.write(audio_data)
        temp_path = temp.name

    try:
        result = model.generate(temp_path)

        return {
            "success": True,
            "text": result.text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)