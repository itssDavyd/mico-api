import whisper

MODEL = whisper.load_model("small")


def transcribe_audio(file_path):
    result = MODEL.transcribe(file_path, language="es", fp16=False)
    text = result["text"]

    return text
