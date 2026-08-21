"""
backend/utils/audio.py
----------------------
Audio utility helpers for Speech-To-Text (STT) and Text-To-Speech (TTS).
"""
import logging
import os
import tempfile
from gtts import gTTS
import speech_recognition as sr

logger = logging.getLogger(__name__)


def transcribe_audio_file(file_bytes: bytes) -> str:
    """
    Transcribe raw audio file bytes into text using SpeechRecognition.
    Supports standard audio formats (WAV, FLAC, AIFF).
    """
    recognizer = sr.Recognizer()
    
    # Save audio bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(file_bytes)
        temp_audio_path = temp_audio.name
        
    try:
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            logger.info("Audio transcribed successfully: %s", text)
            return text
    except sr.UnknownValueError:
        logger.warning("SpeechRecognition could not understand audio.")
        raise ValueError("Could not understand the audio. Please speak clearly.")
    except sr.RequestError as e:
        logger.error("SpeechRecognition request error: %s", e)
        raise ValueError("Speech recognition service is currently unavailable.")
    except Exception as e:
        logger.error("General error during audio transcription: %s", e)
        # Attempt a raw character size fallback or throw helpful error
        raise ValueError(f"Audio file format not supported or invalid. Error: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except Exception:
                pass


def synthesize_text_to_speech(text: str, filename: str, lang: str = "en") -> str:
    """
    Synthesize text into speech using Google Text-to-Speech (gTTS).
    Saves the output to the static cache directory.
    
    Returns the relative web path of the generated audio file.
    """
    cache_dir = "./data/cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    file_path = os.path.join(cache_dir, filename)
    
    # Map general language codes if necessary
    gtts_lang = lang.split("-")[0]  # e.g., 'en-US' -> 'en'
    
    try:
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(file_path)
        logger.info("Speech synthesized successfully at %s", file_path)
        return f"/cache/{filename}"
    except Exception as e:
        logger.error("TTS generation error: %s", e)
        # Return none or placeholder if TTS fails
        return ""
