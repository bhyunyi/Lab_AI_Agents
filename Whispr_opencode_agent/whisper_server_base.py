from fastapi import FastAPI, UploadFile, File
import mlx_whisper
import tempfile
import os

app = FastAPI()

WHISPER_MODEL = "/Users/Shared/models/mlx/whisper-base-mlx"


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):

    # Create temporary audio file
    suffix = os.path.splitext(audio.filename)[1] or ".wav"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:
        audio_data = await audio.read()
        temp.write(audio_data)
        temp_path = temp.name

    try:
        # Run Whisper
        result = mlx_whisper.transcribe(
            temp_path,
            path_or_hf_repo=WHISPER_MODEL
        )

        text = result.get("text", "").strip()

        return {
            "success": True,
            "text": text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)