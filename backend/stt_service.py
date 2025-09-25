from faster_whisper import WhisperModel

# Load model once when the service starts
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file and return the text.
    """
    segments, info = model.transcribe(file_path)
    text = " ".join([segment.text for segment in segments])
    return text
