import asyncio
import json
import base64
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sounddevice as sd
import numpy as np
import websockets
from dotenv import load_dotenv
import os
import logging
from google.cloud import speech
import pyaudio
import requests
import time
from datetime import datetime
from pathlib import Path
import struct
import re

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Keys from .env
MURF_API_KEY = os.getenv("MURF_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Set Google credentials
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# Murf URLs
MURF_WS_URL = "wss://api.murf.ai/v1/speech/stream-input"
MURF_TRANSLATE_URL = "https://api.murf.ai/v1/text/translate"

# Audio storage folders
OUTGOING_AUDIO_FOLDER = "outgoing_translations"
INCOMING_AUDIO_FOLDER = "incoming_translations"

# Supported languages
SUPPORTED_LANGUAGES = {
    "English (US)": {
        "stt_code": "en-US",
        "murf_translate_code": "en-US",
        "voices": {
            "Natalie (Female)": "en-US-natalie",
            "Miles (Male)": "en-US-miles",
            "Ken (Male)": "en-US-ken",
            "Clint (Male)": "en-US-clint",
            "Amara (Female)": "en-US-amara"
        }
    },
    "English (UK)": {
        "stt_code": "en-GB",
        "murf_translate_code": "en-UK",
        "voices": {
            "Ruby (Female)": "en-UK-ruby",
            "Oliver (Male)": "en-UK-oliver"
        }
    },
    "English (India)": {
        "stt_code": "en-IN",
        "murf_translate_code": "en-IN",
        "voices": {
            "Priya (Female)": "en-IN-priya",
            "Rahul (Male)": "en-IN-rahul"
        }
    },
    "Hindi": {
        "stt_code": "hi-IN",
        "murf_translate_code": "hi-IN",
        "voices": {
            "Kabir (Male)": "hi-IN-kabir",
            "Ayushi (Female)": "hi-IN-ayushi",
            "Shaan (Male)": "hi-IN-shaan",
            "Shweta (Female)": "hi-IN-shweta"
        }
    },
    "Tamil": {
        "stt_code": "ta-IN",
        "murf_translate_code": "ta-IN",
        "voices": {
            "Iniya (Female)": "ta-IN-iniya",
            "Suresh (Male)": "ta-IN-suresh"
        }
    },
    "Bengali": {
        "stt_code": "bn-IN",
        "murf_translate_code": "bn-IN",
        "voices": {
            "Anwesha (Female)": "bn-IN-anwesha",
            "Abhik (Male)": "bn-IN-abhik"
        }
    },
    "Marathi": {
        "stt_code": "mr-IN",
        "murf_translate_code": "mr-IN",
        "voices": {
            "Mira (Female)": "mr-IN-mira",
            "Aarav (Male)": "mr-IN-aarav"
        }
    },
    "Telugu": {
        "stt_code": "te-IN",
        "murf_translate_code": "te-IN",
        "voices": {
            "Vani (Female)": "te-IN-vani",
            "Ravi (Male)": "te-IN-ravi"
        }
    },
    "Kannada": {
        "stt_code": "kn-IN",
        "murf_translate_code": "kn-IN",
        "voices": {
            "Deepa (Female)": "kn-IN-deepa",
            "Kiran (Male)": "kn-IN-kiran"
        }
    },
    "Gujarati": {
        "stt_code": "gu-IN",
        "murf_translate_code": "gu-IN",
        "voices": {
            "Diya (Female)": "gu-IN-diya",
            "Jay (Male)": "gu-IN-jay"
        }
    },
    "Spanish (Spain)": {
        "stt_code": "es-ES",
        "murf_translate_code": "es-ES",
        "voices": {
            "Sofia (Female)": "es-ES-sofia",
            "Carlos (Male)": "es-ES-carlos"
        }
    },
    "French": {
        "stt_code": "fr-FR",
        "murf_translate_code": "fr-FR",
        "voices": {
            "Isabelle (Female)": "fr-FR-isabelle",
            "Pierre (Male)": "fr-FR-pierre"
        }
    },
    "German": {
        "stt_code": "de-DE",
        "murf_translate_code": "de-DE",
        "voices": {
            "Anna (Female)": "de-DE-anna",
            "Klaus (Male)": "de-DE-klaus"
        }
    }
}


class BidirectionalVoiceTranslator:
    def __init__(self):
        self.is_running = False
        self.outgoing_text_queue = queue.Queue()
        self.incoming_text_queue = queue.Queue()
        self.audio_level_callback = None
        
        # Track last processed text to prevent duplicates
        self.last_outgoing_text = ""
        self.last_outgoing_time = 0
        self.last_incoming_text = ""
        self.last_incoming_time = 0
        self.duplicate_threshold = 20.0
        
        # Track outgoing translated text to prevent echo loop
        self.last_outgoing_translated_text = ""
        self.last_outgoing_translated_time = 0
        self.echo_threshold = 10.0
        
        # Create audio storage folders
        self.outgoing_folder = Path(OUTGOING_AUDIO_FOLDER)
        self.incoming_folder = Path(INCOMING_AUDIO_FOLDER)
        self.outgoing_folder.mkdir(exist_ok=True)
        self.incoming_folder.mkdir(exist_ok=True)
        logger.info(f"📁 Outgoing audio folder: {self.outgoing_folder.absolute()}")
        logger.info(f"📁 Incoming audio folder: {self.incoming_folder.absolute()}")
        
        # Google Speech Client
        try:
            self.speech_client = speech.SpeechClient()
            logger.info("✅ Google Speech-to-Text initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Speech: {e}")
            raise Exception("Google Cloud credentials not configured properly. Check your .env file.")
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = int(self.sample_rate / 10)
        self.channels = 1
        
        # Device IDs and their supported sample rates
        self.output_device = None
        self.output_device_sample_rate = 44100
        self.input_device = None
        self.speaker_device = None
        self.speaker_device_sample_rate = 44100
        
        # Murf audio settings
        self.murf_sample_rate = 44100
        self.murf_format = "WAV"
        self.murf_channel_type = "MONO"
        
        # PyAudio instances
        self.pyaudio_instance = pyaudio.PyAudio()
        self.mic_stream = None
        self.virtual_input_stream = None
        self.virtual_output_stream = None
        self.speaker_stream = None
        
        # Get available audio devices
        self.output_devices = self.get_output_devices()
        self.input_devices = self.get_input_devices()
        
        logger.info("✅ BidirectionalVoiceTranslator initialized")
    
    def is_duplicate_text(self, text, last_text, last_time, source="unknown"):
        """Check if text is a duplicate of recently processed text"""
        current_time = time.time()
        time_diff = current_time - last_time
        
        # If no previous text, it's not a duplicate
        if not last_text or time_diff > self.duplicate_threshold:
            return False
        
        # Aggressive normalization
        def normalize(s):
            s = re.sub(r'[^\w\s]', '', s)  # Remove punctuation
            s = re.sub(r'\s+', ' ', s)      # Normalize whitespace
            return s.strip().lower()
        
        text_normalized = normalize(text)
        last_text_normalized = normalize(last_text)
        
        # Empty after normalization
        if not text_normalized or not last_text_normalized:
            return False
        
        # Exact match after normalization
        if text_normalized == last_text_normalized:
            logger.info(f"🚫 EXACT DUPLICATE from {source}: '{text[:40]}' (within {time_diff:.1f}s)")
            return True
        
        # One contains the other (substring match)
        if text_normalized in last_text_normalized or last_text_normalized in text_normalized:
            # Calculate length ratio
            shorter_len = min(len(text_normalized), len(last_text_normalized))
            longer_len = max(len(text_normalized), len(last_text_normalized))
            
            if shorter_len > 0:
                similarity = shorter_len / longer_len
                
                # If 90% similar, it's a duplicate
                if similarity >= 0.9:
                    logger.info(f"🚫 SIMILAR DUPLICATE from {source}: '{text[:40]}' (similarity: {similarity:.0%}, within {time_diff:.1f}s)")
                    return True
        
        return False
    
    def is_echo(self, incoming_text):
        """Check if incoming text is an echo of what we just sent out"""
        current_time = time.time()
        time_diff = current_time - self.last_outgoing_translated_time
        
        # If we haven't sent anything recently, it's not an echo
        if not self.last_outgoing_translated_text or time_diff > self.echo_threshold:
            return False
        
        # Normalize both texts
        def normalize(s):
            s = re.sub(r'[^\w\s]', '', s)  # Remove punctuation
            s = re.sub(r'\s+', ' ', s)      # Normalize whitespace
            return s.strip().lower()
        
        incoming_normalized = normalize(incoming_text)
        outgoing_normalized = normalize(self.last_outgoing_translated_text)
        
        # Check if they match or are very similar
        if incoming_normalized == outgoing_normalized:
            logger.info(f"🔇 ECHO match: Incoming='{incoming_text[:30]}' vs Outgoing='{self.last_outgoing_translated_text[:30]}'")
            return True
        
        # Check substring match (85% similarity for echo detection)
        if incoming_normalized in outgoing_normalized or outgoing_normalized in incoming_normalized:
            shorter_len = min(len(incoming_normalized), len(outgoing_normalized))
            longer_len = max(len(incoming_normalized), len(outgoing_normalized))
            
            if shorter_len > 0:
                similarity = shorter_len / longer_len
                if similarity >= 0.85:
                    logger.info(f"🔇 ECHO similarity match: {similarity:.0%} within {time_diff:.1f}s")
                    return True
        
        return False
    
    def get_supported_sample_rate(self, device_index, is_input=False):
        """Get the supported sample rate for a device"""
        try:
            device_info = self.pyaudio_instance.get_device_info_by_index(device_index)
            default_sample_rate = int(device_info['defaultSampleRate'])
            
            test_rates = [16000, 48000, 44100, 32000, 24000, 22050, 11025, 8000]
            
            for rate in test_rates:
                try:
                    if is_input:
                        if self.pyaudio_instance.is_format_supported(
                            rate,
                            input_device=device_index,
                            input_channels=1,
                            input_format=pyaudio.paInt16
                        ):
                            logger.info(f"   ✓ Device {device_index} supports {rate}Hz (input)")
                            return rate
                    else:
                        if self.pyaudio_instance.is_format_supported(
                            rate,
                            output_device=device_index,
                            output_channels=1,
                            output_format=pyaudio.paInt16
                        ):
                            logger.info(f"   ✓ Device {device_index} supports {rate}Hz (output)")
                            return rate
                except:
                    continue
            
            logger.info(f"   ✓ Using default rate {default_sample_rate}Hz for device {device_index}")
            return default_sample_rate
            
        except Exception as e:
            logger.warning(f"   ⚠️ Could not determine sample rate for device {device_index}, defaulting to 16000Hz")
            return 16000
    
    def resample_audio(self, audio_data, original_rate, target_rate):
        """Resample audio data to target sample rate"""
        if original_rate == target_rate:
            return audio_data
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            ratio = target_rate / original_rate
            new_length = int(len(audio_array) * ratio)
            resampled = np.interp(
                np.linspace(0, len(audio_array) - 1, new_length),
                np.arange(len(audio_array)),
                audio_array
            ).astype(np.int16)
            
            return resampled.tobytes()
        except Exception as e:
            logger.error(f"   ❌ Resampling failed: {e}")
            return audio_data
    
    def get_output_devices(self):
        """Get list of available output audio devices"""
        devices = sd.query_devices()
        output_devices = {}
        logger.info("🔊 Available OUTPUT devices:")
        for idx, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                output_devices[device['name']] = idx
                logger.info(f"  [{idx}] {device['name']}")
        return output_devices
    
    def get_input_devices(self):
        """Get list of available input audio devices"""
        devices = sd.query_devices()
        input_devices = {}
        logger.info("🎤 Available INPUT devices:")
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices[device['name']] = idx
                logger.info(f"  [{idx}] {device['name']}")
        return input_devices
    
    def set_output_device(self, device_name):
        """Set the output device (Virtual Cable - for speaking to meeting)"""
        if device_name in self.output_devices:
            self.output_device = self.output_devices[device_name]
            logger.info(f"✅ OUTPUT device set to: {device_name} (Device ID: {self.output_device})")
            
            self.output_device_sample_rate = self.get_supported_sample_rate(self.output_device, is_input=False)
            
            try:
                if self.virtual_output_stream:
                    self.virtual_output_stream.close()
                
                self.virtual_output_stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.output_device_sample_rate,
                    output=True,
                    output_device_index=self.output_device,
                    frames_per_buffer=1024
                )
                logger.info(f"✅ Virtual OUTPUT stream opened at {self.output_device_sample_rate}Hz")
            except Exception as e:
                logger.error(f"❌ Failed to open virtual output stream: {e}")
            
            return True
        return False
    
    def set_input_device(self, device_name):
        """Set the input device (Virtual Cable - for hearing from meeting)"""
        if device_name in self.input_devices:
            self.input_device = self.input_devices[device_name]
            logger.info(f"✅ INPUT device set to: {device_name} (Device ID: {self.input_device})")
            return True
        return False
    
    def set_speaker_device(self, device_name):
        """Set the speaker device (Real speakers - for hearing translations)"""
        if device_name in self.output_devices:
            self.speaker_device = self.output_devices[device_name]
            logger.info(f"✅ SPEAKER device set to: {device_name} (Device ID: {self.speaker_device})")
            
            self.speaker_device_sample_rate = self.get_supported_sample_rate(self.speaker_device, is_input=False)
            
            try:
                if self.speaker_stream:
                    self.speaker_stream.close()
                
                self.speaker_stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.speaker_device_sample_rate,
                    output=True,
                    output_device_index=self.speaker_device,
                    frames_per_buffer=1024
                )
                logger.info(f"✅ Speaker stream opened at {self.speaker_device_sample_rate}Hz")
            except Exception as e:
                logger.error(f"❌ Failed to open speaker stream: {e}")
            
            return True
        return False
    
    def play_audio_to_device(self, audio_bytes, device_stream, device_name, target_sample_rate):
        """Play audio to specified device with resampling if needed"""
        try:
            if not device_stream:
                logger.error(f"❌ {device_name} stream not initialized!")
                return False
            
            if not audio_bytes or len(audio_bytes) == 0:
                logger.warning("⚠️ No audio data to play")
                return False
            
            if self.murf_sample_rate != target_sample_rate:
                audio_bytes = self.resample_audio(audio_bytes, self.murf_sample_rate, target_sample_rate)
            
            device_stream.write(audio_bytes)
            
            return True
        except Exception as e:
            logger.error(f"❌ Error playing audio to {device_name}: {e}")
            return False
    
    def save_audio_to_file(self, audio_data, text, language, folder):
        """Save audio data to a WAV file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            clean_text = "".join(c for c in text if c.isalnum() or c.isspace())[:30]
            clean_text = clean_text.replace(" ", "_")
            
            filename = f"{timestamp}_{language}_{clean_text}.wav"
            filepath = folder / filename
            
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"💾 Audio saved: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None
    
    def translate_with_murf(self, text, source_lang_code, target_lang_code, callback):
        """Translate text using Murf Translation API"""
        if source_lang_code == target_lang_code:
            logger.info("ℹ️ Same language, no translation needed")
            return text
        
        try:
            headers = {
                "api-key": MURF_API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "target_language": target_lang_code,
                "texts": [text]
            }
            
            logger.info(f"🔄 Translating: {source_lang_code} → {target_lang_code}")
            
            response = requests.post(
                MURF_TRANSLATE_URL,
                headers=headers,
                json=payload,
                timeout=8
            )
            
            if response.status_code == 200:
                result = response.json()
                translations = result.get("translations", [])
                
                if translations and len(translations) > 0:
                    translated_text = translations[0].get("translated_text", "")
                    if translated_text:
                        logger.info(f"✅ Translated: '{text[:30]}' → '{translated_text[:30]}'")
                        return translated_text
                
                logger.warning("⚠️ Translation response empty")
                return text
            else:
                error_msg = response.text
                logger.error(f"❌ Translation error ({response.status_code}): {error_msg}")
                return text
                
        except requests.Timeout:
            logger.error("❌ Translation timeout")
            return text
        except Exception as e:
            logger.error(f"❌ Translation error: {e}")
            return text
    
    async def synthesize_with_websocket(self, voice_id, text, language, device_stream, device_name, target_sample_rate, folder):
        """Synthesize speech using Murf WebSocket and play to specified device"""
        ws = None
        complete_audio = bytearray()
        
        try:
            url = f"{MURF_WS_URL}?api-key={MURF_API_KEY}&sample_rate={self.murf_sample_rate}&channel_type={self.murf_channel_type}&format={self.murf_format}"
            
            ws = await asyncio.wait_for(
                websockets.connect(url, ping_interval=20, ping_timeout=10),
                timeout=5.0
            )
            
            voice_config_msg = {
                "voice_config": {
                    "voiceId": voice_id,
                    "style": "Conversational",
                    "rate": 15,
                    "pitch": 0,
                    "variation": 1
                }
            }
            
            await ws.send(json.dumps(voice_config_msg))
            
            text_msg = {
                "text": text,
                "end": True
            }
            
            await ws.send(json.dumps(text_msg))
            
            first_chunk = True
            chunk_count = 0
            
            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=8.0)
                    data = json.loads(response)
                    
                    if "audio" in data:
                        audio_b64 = data["audio"]
                        if audio_b64:
                            audio_bytes = base64.b64decode(audio_b64)
                            
                            if first_chunk and len(audio_bytes) > 44:
                                audio_bytes = audio_bytes[44:]
                                first_chunk = False
                            
                            if len(audio_bytes) > 0:
                                chunk_count += 1
                                complete_audio.extend(audio_bytes)
                                self.play_audio_to_device(audio_bytes, device_stream, device_name, target_sample_rate)
                    
                    if data.get("final"):
                        break
                    
                    if "error" in data:
                        logger.error(f"❌ WebSocket error: {data['error']}")
                        break
                        
                except asyncio.TimeoutError:
                    if chunk_count > 0:
                        break
                    else:
                        return None
            
            if len(complete_audio) > 0:
                wav_data = self.create_wav_file(bytes(complete_audio))
                self.save_audio_to_file(wav_data, text, language, folder)
                return wav_data
            
            return None
            
        except asyncio.TimeoutError:
            logger.error("❌ WebSocket connection timeout")
            return None
        except Exception as e:
            logger.error(f"❌ WebSocket synthesis error: {e}")
            return None
        finally:
            if ws:
                try:
                    await ws.close()
                except:
                    pass
    
    def create_wav_file(self, audio_data):
        """Create a proper WAV file with header"""
        num_channels = 1
        sample_width = 2
        sample_rate = self.murf_sample_rate
        
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + len(audio_data),
            b'WAVE',
            b'fmt ',
            16, 1, num_channels, sample_rate,
            sample_rate * num_channels * sample_width,
            num_channels * sample_width,
            sample_width * 8,
            b'data',
            len(audio_data)
        )
        
        return wav_header + audio_data
    
    def _outgoing_stt_thread(self, source_lang_code, callback):
        """Listen to YOUR microphone with auto-restart"""
        while self.is_running:
            def audio_generator():
                while self.is_running:
                    try:
                        chunk = self.mic_stream.read(self.chunk_size, exception_on_overflow=False)
                        
                        # Calculate audio level
                        audio_array = np.frombuffer(chunk, dtype=np.int16)
                        audio_level = np.abs(audio_array).mean()
                        if self.audio_level_callback:
                            self.audio_level_callback("mic", audio_level)
                        
                        yield chunk
                    except Exception as e:
                        logger.error(f"Error in mic audio generator: {e}")
                        break
            
            try:
                if not self.mic_stream or not self.mic_stream.is_active():
                    self.mic_stream = self.pyaudio_instance.open(
                        format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk_size
                    )
                
                logger.info(f"✅ Listening to YOUR microphone in {source_lang_code}")
                callback("🎤 Listening to YOUR voice...")
                
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate,
                    language_code=source_lang_code,
                    enable_automatic_punctuation=True,
                    model="default"
                )
                
                streaming_config = speech.StreamingRecognitionConfig(
                    config=config,
                    interim_results=False,
                    single_utterance=False
                )
                
                audio_generator_iter = audio_generator()
                requests_iter = (speech.StreamingRecognizeRequest(audio_content=content)
                               for content in audio_generator_iter)
                
                responses = self.speech_client.streaming_recognize(streaming_config, requests_iter)
                
                for response in responses:
                    if not self.is_running:
                        break
                    
                    for result in response.results:
                        if result.is_final:
                            transcript = result.alternatives[0].transcript
                            if transcript.strip():
                                if not self.is_duplicate_text(
                                    transcript, 
                                    self.last_outgoing_text, 
                                    self.last_outgoing_time,
                                    "YOUR MIC"
                                ):
                                    logger.info(f"🎙️ YOU said: {transcript}")
                                    self.last_outgoing_text = transcript
                                    self.last_outgoing_time = time.time()
                                    self.outgoing_text_queue.put(transcript)
                                    callback(f"📢 You: {transcript[:50]}...")
                
            except Exception as e:
                if self.is_running:
                    logger.error(f"Outgoing STT error: {e}")
                    logger.info("🔄 Restarting outgoing STT in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    break
            finally:
                if self.mic_stream:
                    try:
                        self.mic_stream.stop_stream()
                        self.mic_stream.close()
                        self.mic_stream = None
                    except:
                        pass
    
    def _incoming_stt_thread(self, target_lang_code, callback):
        """Listen to meeting audio with auto-restart"""
        while self.is_running:
            # Detect device sample rate
            try:
                device_info = self.pyaudio_instance.get_device_info_by_index(self.input_device)
                native_rate = int(device_info['defaultSampleRate'])
                logger.info(f"📊 Virtual Cable native rate: {native_rate}Hz")
                
                test_rates = [native_rate, 48000, 44100, 16000]
                device_sample_rate = None
                
                for rate in test_rates:
                    try:
                        test_stream = self.pyaudio_instance.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=rate,
                            input=True,
                            input_device_index=self.input_device,
                            frames_per_buffer=int(rate / 10)
                        )
                        test_stream.close()
                        device_sample_rate = rate
                        logger.info(f"✅ Virtual Cable supports {rate}Hz")
                        break
                    except:
                        continue
                
                if not device_sample_rate:
                    logger.error("❌ Could not find compatible sample rate!")
                    callback("❌ Virtual Cable error!", error=True)
                    break
                
            except Exception as e:
                logger.error(f"❌ Error detecting device sample rate: {e}")
                if self.is_running:
                    time.sleep(2)
                    continue
                else:
                    break
            
            device_chunk_size = int(device_sample_rate / 10)
            
            def audio_generator():
                while self.is_running:
                    try:
                        chunk = self.virtual_input_stream.read(
                            device_chunk_size, 
                            exception_on_overflow=False
                        )
                        
                        audio_array = np.frombuffer(chunk, dtype=np.int16)
                        audio_level = np.abs(audio_array).mean()
                        if self.audio_level_callback:
                            self.audio_level_callback("meeting", audio_level)
                        
                        if device_sample_rate != 16000:
                            ratio = 16000 / device_sample_rate
                            new_length = int(len(audio_array) * ratio)
                            resampled = np.interp(
                                np.linspace(0, len(audio_array) - 1, new_length),
                                np.arange(len(audio_array)),
                                audio_array
                            ).astype(np.int16)
                            yield resampled.tobytes()
                        else:
                            yield chunk
                            
                    except Exception as e:
                        logger.error(f"Error reading virtual input: {e}")
                        break
            
            try:
                logger.info(f"🔌 Opening virtual input stream at {device_sample_rate}Hz...")
                
                if not self.virtual_input_stream or not self.virtual_input_stream.is_active():
                    self.virtual_input_stream = self.pyaudio_instance.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=device_sample_rate,
                        input=True,
                        input_device_index=self.input_device,
                        frames_per_buffer=device_chunk_size
                    )
                
                logger.info(f"✅ Listening to MEETING AUDIO in {target_lang_code}")
                logger.info(f"📊 Capturing at {device_sample_rate}Hz, resampling to 16000Hz")
                callback(f"🎧 Listening to meeting ({target_lang_code})...")
                
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code=target_lang_code,
                    enable_automatic_punctuation=True,
                    model="latest_long",
                    use_enhanced=True
                )
                
                streaming_config = speech.StreamingRecognitionConfig(
                    config=config,
                    interim_results=False,
                    single_utterance=False
                )
                
                audio_generator_iter = audio_generator()
                requests_iter = (speech.StreamingRecognizeRequest(audio_content=content)
                               for content in audio_generator_iter)
                
                logger.info("🎧 Starting Google STT streaming for meeting audio...")
                responses = self.speech_client.streaming_recognize(streaming_config, requests_iter)
                
                for response in responses:
                    if not self.is_running:
                        break
                    
                    for result in response.results:
                        if result.is_final:
                            transcript = result.alternatives[0].transcript
                            if transcript.strip():
                                if self.is_echo(transcript):
                                    logger.info(f"🔇 ECHO blocked: '{transcript[:40]}'")
                                    continue
                                
                                if not self.is_duplicate_text(
                                    transcript, 
                                    self.last_incoming_text, 
                                    self.last_incoming_time,
                                    "MEETING"
                                ):
                                    logger.info(f"🎧 THEY said: {transcript}")
                                    self.last_incoming_text = transcript
                                    self.last_incoming_time = time.time()
                                    self.incoming_text_queue.put(transcript)
                                    callback(f"👥 Them: {transcript[:50]}...")
                
            except Exception as e:
                if self.is_running:
                    logger.error(f"Incoming STT error: {e}")
                    logger.info("🔄 Restarting incoming STT in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    break
            finally:
                if self.virtual_input_stream:
                    try:
                        self.virtual_input_stream.stop_stream()
                        self.virtual_input_stream.close()
                        self.virtual_input_stream = None
                    except:
                        pass
    
    def _outgoing_translation_thread(self, source_lang, target_lang, voice_id, 
                                    source_lang_code, target_lang_code, callback):
        """OUTGOING: YOUR language → THEIR language → Meeting"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.is_running:
                try:
                    original_text = self.outgoing_text_queue.get(timeout=0.2)
                except queue.Empty:
                    continue
                
                callback(f"📢 You ({source_lang}): {original_text}")
                start_time = time.time()
                
                translated_text = self.translate_with_murf(
                    original_text, source_lang_code, target_lang_code, callback
                )
                
                if translated_text is None:
                    translated_text = original_text
                
                if translated_text != original_text:
                    callback(f"💬 To meeting ({target_lang}): {translated_text}")
                
                callback("🎤 Generating speech...")
                
                self.last_outgoing_translated_text = translated_text
                self.last_outgoing_translated_time = time.time()
                
                audio_data = loop.run_until_complete(
                    self.synthesize_with_websocket(
                        voice_id, translated_text, target_lang, 
                        self.virtual_output_stream, "Virtual Cable",
                        self.output_device_sample_rate,
                        self.outgoing_folder
                    )
                )
                
                total_latency = time.time() - start_time
                
                if audio_data:
                    callback(f"📡 Sent! (⚡ {total_latency:.2f}s)")
                    
                    if audio_data and len(audio_data) > 44:
                        audio_duration = (len(audio_data) - 44) / (self.murf_sample_rate * 2 * 1)
                        time.sleep(min(audio_duration + 0.3, 3.0))
                else:
                    callback("⚠️ Failed!", error=True)
        
        except Exception as e:
            logger.error(f"Outgoing translation thread error: {e}")
        finally:
            loop.close()
    
    def _incoming_translation_thread(self, source_lang, target_lang, voice_id_to_you,
                                    source_lang_code, target_lang_code, callback):
        """INCOMING: THEIR language → YOUR language → Speakers"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.is_running:
                try:
                    original_text = self.incoming_text_queue.get(timeout=0.2)
                except queue.Empty:
                    continue
                
                callback(f"👥 Them ({target_lang}): {original_text}")
                start_time = time.time()
                
                translated_text = self.translate_with_murf(
                    original_text, 
                    target_lang_code,
                    source_lang_code,
                    callback
                )
                
                if translated_text is None:
                    translated_text = original_text
                
                if translated_text != original_text:
                    callback(f"💬 For you ({source_lang}): {translated_text}")
                
                callback("🔊 Playing...")
                
                audio_data = loop.run_until_complete(
                    self.synthesize_with_websocket(
                        voice_id_to_you, translated_text, source_lang,
                        self.speaker_stream, "Speakers",
                        self.speaker_device_sample_rate,
                        self.incoming_folder
                    )
                )
                
                total_latency = time.time() - start_time
                
                if audio_data:
                    callback(f"🔊 Heard! (⚡ {total_latency:.2f}s)")
                else:
                    callback("⚠️ Failed!", error=True)
        
        except Exception as e:
            logger.error(f"Incoming translation thread error: {e}")
        finally:
            loop.close()
    
    def start(self, source_lang, target_lang, voice_id_to_meeting, voice_id_to_you, status_callback, audio_level_callback=None):
        """Start the bidirectional translation service"""
        self.is_running = True
        self.audio_level_callback = audio_level_callback
        
        # Reset tracking
        self.last_outgoing_text = ""
        self.last_outgoing_time = 0
        self.last_incoming_text = ""
        self.last_incoming_time = 0
        self.last_outgoing_translated_text = ""
        self.last_outgoing_translated_time = 0
        
        source_info = SUPPORTED_LANGUAGES[source_lang]
        target_info = SUPPORTED_LANGUAGES[target_lang]
        
        source_lang_code = source_info["stt_code"]
        target_lang_code = target_info["murf_translate_code"]
        
        logger.info(f"🚀 Starting BIDIRECTIONAL translation:")
        logger.info(f"  📤 OUTGOING: YOU speak {source_lang} → {target_lang} → Meeting")
        logger.info(f"  📥 INCOMING: THEY speak {target_lang} → {source_lang} → You")
        
        if not self.virtual_output_stream:
            logger.error("❌ Virtual output stream not initialized!")
            status_callback("❌ Output device not set!", error=True)
            self.is_running = False
            return
        
        if not self.speaker_stream:
            logger.error("❌ Speaker stream not initialized!")
            status_callback("❌ Speaker device not set!", error=True)
            self.is_running = False
            return
        
        # Clear queues
        while not self.outgoing_text_queue.empty():
            try:
                self.outgoing_text_queue.get_nowait()
            except:
                break
        
        while not self.incoming_text_queue.empty():
            try:
                self.incoming_text_queue.get_nowait()
            except:
                break
        
        # Start all threads
        threading.Thread(
            target=self._outgoing_stt_thread,
            args=(source_lang_code, status_callback),
            daemon=True
        ).start()
        
        threading.Thread(
            target=self._incoming_stt_thread,
            args=(target_lang_code, status_callback),
            daemon=True
        ).start()
        
        threading.Thread(
            target=self._outgoing_translation_thread,
            args=(source_lang, target_lang, voice_id_to_meeting,
                  source_lang_code, target_lang_code, status_callback),
            daemon=True
        ).start()
        
        threading.Thread(
            target=self._incoming_translation_thread,
            args=(source_lang, target_lang, voice_id_to_you,
                  source_lang_code, target_lang_code, status_callback),
            daemon=True
        ).start()
        
        status_callback("✅ Bidirectional translation active!")
    
    def stop(self):
        """Stop the translation service"""
        logger.info("ℹ️ Stopping bidirectional translation service...")
        self.is_running = False
        self.audio_level_callback = None
        
        # Reset tracking
        self.last_outgoing_text = ""
        self.last_outgoing_time = 0
        self.last_incoming_text = ""
        self.last_incoming_time = 0
        self.last_outgoing_translated_text = ""
        self.last_outgoing_translated_time = 0
        
        if self.mic_stream:
            try:
                self.mic_stream.stop_stream()
                self.mic_stream.close()
                self.mic_stream = None
            except:
                pass
        
        if self.virtual_input_stream:
            try:
                self.virtual_input_stream.stop_stream()
                self.virtual_input_stream.close()
                self.virtual_input_stream = None
            except:
                pass
        
        time.sleep(0.5)
        logger.info("✅ Bidirectional translation service stopped")
    
    def cleanup(self):
        """Full cleanup"""
        self.stop()
        
        if self.virtual_output_stream:
            try:
                self.virtual_output_stream.stop_stream()
                self.virtual_output_stream.close()
            except:
                pass
        
        if self.speaker_stream:
            try:
                self.speaker_stream.stop_stream()
                self.speaker_stream.close()
            except:
                pass
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()


class TranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌉 VoiceBridge - Bidirectional Real-Time Voice Translator")
        self.root.geometry("1100x950")
        
        if not MURF_API_KEY:
            messagebox.showerror("API Key Missing", "Please set MURF_API_KEY in your .env file")
            self.root.destroy()
            return
        
        if not GOOGLE_APPLICATION_CREDENTIALS:
            messagebox.showerror("Google Credentials Missing", 
                               "Please set GOOGLE_APPLICATION_CREDENTIALS path in your .env file")
            self.root.destroy()
            return
        
        try:
            self.translator = BidirectionalVoiceTranslator()
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.root.destroy()
            return
        
        self.is_running = False
        self.setup_ui()
    
    def audio_level_callback(self, source, level):
        """Update audio level indicators"""
        normalized_level = min(100, int(level / 100))
        
        if source == "mic":
            self.root.after(0, lambda: self.mic_level_bar.config(value=normalized_level))
        elif source == "meeting":
            self.root.after(0, lambda: self.meeting_level_bar.config(value=normalized_level))
    
    def setup_ui(self):
        """Setup the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Title
        title_frame = tk.Frame(self.root, bg="#1a1a2e", height=80)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🌉 VoiceBridge - Bidirectional Translation\n⚡ Auto-Restart | Low Latency | No Echo",
            font=("Arial", 12, "bold"),
            bg="#1a1a2e",
            fg="#00d4ff",
            justify=tk.CENTER
        )
        title_label.pack(pady=15)
        
        # Create main canvas with scrollbar
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f8f9fa")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_frame = self.scrollable_frame
        main_frame.config(padx=20, pady=20)
        
        # Audio Level Indicators
        level_frame = tk.LabelFrame(main_frame, text="🎙️ Audio Level Indicators", 
                                    font=("Arial", 10, "bold"), padx=15, pady=10)
        level_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(level_frame, text="Your Microphone:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mic_level_bar = ttk.Progressbar(level_frame, length=300, mode='determinate')
        self.mic_level_bar.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(level_frame, text="Meeting Audio:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.meeting_level_bar = ttk.Progressbar(level_frame, length=300, mode='determinate')
        self.meeting_level_bar.grid(row=1, column=1, padx=10, pady=5)
        
        # Language Selection
        lang_frame = tk.LabelFrame(main_frame, text="🗣️ Language Selection", 
                                   font=("Arial", 11, "bold"), padx=15, pady=15)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(lang_frame, text="I speak:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_lang_var = tk.StringVar(value="English (US)")
        source_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.source_lang_var,
            values=list(SUPPORTED_LANGUAGES.keys()),
            state="readonly",
            width=28,
            font=("Arial", 9)
        )
        source_dropdown.grid(row=0, column=1, padx=10, pady=5)
        source_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)
        
        tk.Label(lang_frame, text="They speak:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_lang_var = tk.StringVar(value="Hindi")
        target_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.target_lang_var,
            values=list(SUPPORTED_LANGUAGES.keys()),
            state="readonly",
            width=28,
            font=("Arial", 9)
        )
        target_dropdown.grid(row=1, column=1, padx=10, pady=5)
        target_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Voice Selection
        tk.Label(lang_frame, text="Voice to meeting:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.voice_to_meeting_var = tk.StringVar()
        self.voice_to_meeting_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.voice_to_meeting_var,
            state="readonly",
            width=28,
            font=("Arial", 9)
        )
        self.voice_to_meeting_dropdown.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(lang_frame, text="Voice to you:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.voice_to_you_var = tk.StringVar()
        self.voice_to_you_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.voice_to_you_var,
            state="readonly",
            width=28,
            font=("Arial", 9)
        )
        self.voice_to_you_dropdown.grid(row=3, column=1, padx=10, pady=5)
        
        self.on_language_change()
        
        # Audio Device Selection
        device_frame = tk.LabelFrame(main_frame, text="🔊 Audio Devices", 
                                     font=("Arial", 11, "bold"), padx=15, pady=15)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(device_frame, text="1️⃣ Virtual Cable OUT:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_device_var = tk.StringVar()
        output_dropdown = ttk.Combobox(
            device_frame,
            textvariable=self.output_device_var,
            values=list(self.translator.output_devices.keys()),
            state="readonly",
            width=42,
            font=("Arial", 8)
        )
        output_dropdown.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        output_dropdown.bind("<<ComboboxSelected>>", 
                           lambda e: self.translator.set_output_device(self.output_device_var.get()))
        
        self.test_vb_out_button = tk.Button(
            device_frame,
            text="🧪 Test",
            command=self.test_virtual_cable_output,
            bg="#3498DB",
            fg="white",
            font=("Arial", 8, "bold"),
            cursor="hand2",
            width=8
        )
        self.test_vb_out_button.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(device_frame, text="2️⃣ Virtual Cable IN:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.input_device_var = tk.StringVar()
        input_dropdown = ttk.Combobox(
            device_frame,
            textvariable=self.input_device_var,
            values=list(self.translator.input_devices.keys()),
            state="readonly",
            width=42,
            font=("Arial", 8)
        )
        input_dropdown.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        input_dropdown.bind("<<ComboboxSelected>>", 
                           lambda e: self.translator.set_input_device(self.input_device_var.get()))
        
        tk.Label(device_frame, text="3️⃣ Your Speakers:", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.speaker_device_var = tk.StringVar()
        speaker_dropdown = ttk.Combobox(
            device_frame,
            textvariable=self.speaker_device_var,
            values=list(self.translator.output_devices.keys()),
            state="readonly",
            width=42,
            font=("Arial", 8)
        )
        speaker_dropdown.grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        speaker_dropdown.bind("<<ComboboxSelected>>", 
                           lambda e: self.translator.set_speaker_device(self.speaker_device_var.get()))
        
        self.test_speaker_button = tk.Button(
            device_frame,
            text="🧪 Test",
            command=self.test_speakers,
            bg="#3498DB",
            fg="white",
            font=("Arial", 8, "bold"),
            cursor="hand2",
            width=8
        )
        self.test_speaker_button.grid(row=5, column=1, padx=5, pady=5)
        
        # Auto-select devices
        if self.translator.output_devices:
            vb_cable = next((name for name in self.translator.output_devices.keys() 
                           if 'cable input' in name.lower() and '16' not in name.lower()), None)
            if not vb_cable:
                vb_cable = next((name for name in self.translator.output_devices.keys() 
                               if 'cable input' in name.lower()), None)
            if vb_cable:
                output_dropdown.set(vb_cable)
                self.translator.set_output_device(vb_cable)
        
        if self.translator.input_devices:
            vb_cable_in = next((name for name in self.translator.input_devices.keys() 
                              if 'cable output' in name.lower() and '16' not in name.lower()), None)
            if not vb_cable_in:
                vb_cable_in = next((name for name in self.translator.input_devices.keys() 
                                  if 'cable output' in name.lower()), None)
            if vb_cable_in:
                input_dropdown.set(vb_cable_in)
                self.translator.set_input_device(vb_cable_in)
        
        if self.translator.output_devices:
            real_speaker = next((name for name in self.translator.output_devices.keys() 
                               if 'cable' not in name.lower() and ('realtek' in name.lower() or 'speaker' in name.lower())), None)
            if not real_speaker:
                for name in self.translator.output_devices.keys():
                    if 'cable' not in name.lower():
                        real_speaker = name
                        break
            if real_speaker:
                speaker_dropdown.set(real_speaker)
                self.translator.set_speaker_device(real_speaker)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        status_frame = tk.LabelFrame(main_frame, text="📊 Status", 
                                     font=("Arial", 11, "bold"), padx=15, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame, 
            text="⚡ Ready! Auto-restart enabled", 
            font=("Arial", 10), 
            fg="#27AE60", 
            anchor=tk.W,
            wraplength=950
        )
        self.status_label.pack(fill=tk.X)
        
        # Translation Display
        display_frame = tk.LabelFrame(main_frame, text="💬 Translation Log", 
                                      font=("Arial", 11, "bold"), padx=15, pady=10)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.translation_text = scrolledtext.ScrolledText(
            display_frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 9),
            bg="#f0f0f0"
        )
        self.translation_text.pack(fill=tk.BOTH, expand=True)
        
        # Control Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = tk.Button(
            button_frame,
            text="🟢 Start Translation",
            command=self.toggle_translation,
            bg="#27AE60",
            fg="white",
            font=("Arial", 11, "bold"),
            height=2,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        clear_button = tk.Button(
            button_frame,
            text="🧹 Clear",
            command=self.clear_display,
            bg="#95A5A6",
            fg="white",
            font=("Arial", 11, "bold"),
            height=2,
            cursor="hand2"
        )
        clear_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def test_virtual_cable_output(self):
        """Test virtual cable output"""
        if not self.output_device_var.get():
            messagebox.showwarning("No Device", "Select Virtual Cable OUT first!")
            return
        
        self.translator.set_output_device(self.output_device_var.get())
        self.update_status("🔊 Testing...")
        
        duration = 1.0
        frequency = 440
        t = np.linspace(0, duration, int(44100 * duration))
        test_audio = np.sin(2 * np.pi * frequency * t) * 0.3
        test_audio = (test_audio * 32767).astype(np.int16)
        test_audio_bytes = test_audio.tobytes()
        
        try:
            success = self.translator.play_audio_to_device(
                test_audio_bytes, 
                self.translator.virtual_output_stream, 
                "Virtual Cable OUT",
                self.translator.output_device_sample_rate
            )
            
            if success:
                self.update_status("✅ Test beep sent!")
                messagebox.showinfo("Test Success", "✅ Others in meeting should hear beep!")
            else:
                self.update_status("❌ Failed!", error=True)
        except Exception as e:
            messagebox.showerror("Test Failed", f"Error: {str(e)}")
    
    def test_speakers(self):
        """Test speakers"""
        if not self.speaker_device_var.get():
            messagebox.showwarning("No Device", "Select Speakers first!")
            return
        
        self.translator.set_speaker_device(self.speaker_device_var.get())
        self.update_status("🔊 Testing...")
        
        duration = 1.0
        frequency = 440
        t = np.linspace(0, duration, int(44100 * duration))
        test_audio = np.sin(2 * np.pi * frequency * t) * 0.3
        test_audio = (test_audio * 32767).astype(np.int16)
        test_audio_bytes = test_audio.tobytes()
        
        try:
            success = self.translator.play_audio_to_device(
                test_audio_bytes,
                self.translator.speaker_stream,
                "Speakers",
                self.translator.speaker_device_sample_rate
            )
            
            if success:
                self.update_status("✅ Test beep played!")
                messagebox.showinfo("Test Success", "✅ Did you hear the beep?")
            else:
                self.update_status("❌ Failed!", error=True)
        except Exception as e:
            messagebox.showerror("Test Failed", f"Error: {str(e)}")
    
    def on_language_change(self, event=None):
        """Update voice options"""
        target_lang = self.target_lang_var.get()
        source_lang = self.source_lang_var.get()
        
        if target_lang in SUPPORTED_LANGUAGES:
            voices = list(SUPPORTED_LANGUAGES[target_lang]["voices"].keys())
            self.voice_to_meeting_dropdown['values'] = voices
            if voices:
                self.voice_to_meeting_dropdown.set(voices[0])
        
        if source_lang in SUPPORTED_LANGUAGES:
            voices = list(SUPPORTED_LANGUAGES[source_lang]["voices"].keys())
            self.voice_to_you_dropdown['values'] = voices
            if voices:
                self.voice_to_you_dropdown.set(voices[0])
    
    def update_status(self, message, error=False):
        """Update status"""
        if any(kw in message for kw in ["Translating", "Generating", "Connecting"]):
            self.root.after(0, lambda: self.progress.start(10))
        else:
            self.root.after(0, lambda: self.progress.stop())
        
        color = "#E74C3C" if error else "#27AE60"
        self.root.after(0, lambda: self.status_label.config(text=message, fg=color))
        
        if any(kw in message for kw in 
            ["You", "Them", "Translation", "Sent", "heard", "Listening", "To meeting", "For you", "Playing", "Generating"]):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.root.after(0, lambda m=message, t=timestamp: 
                self.translation_text.insert(tk.END, f"[{t}] {m}\n"))
            self.root.after(0, lambda: self.translation_text.see(tk.END))
    
    def toggle_translation(self):
        """Start/stop translation"""
        if not self.is_running:
            if self.source_lang_var.get() == self.target_lang_var.get():
                messagebox.showwarning("Invalid Selection", "Please select different languages!")
                return
            
            if not all([self.output_device_var.get(), self.input_device_var.get(), 
                       self.speaker_device_var.get()]):
                messagebox.showwarning("Missing Devices", "Please select all 3 audio devices!")
                return
            
            target_lang = self.target_lang_var.get()
            source_lang = self.source_lang_var.get()
            
            voice_to_meeting = SUPPORTED_LANGUAGES[target_lang]["voices"][self.voice_to_meeting_var.get()]
            voice_to_you = SUPPORTED_LANGUAGES[source_lang]["voices"][self.voice_to_you_var.get()]
            
            self.is_running = True
            self.start_button.config(text="🔴 Stop", bg="#E74C3C")
            self.test_vb_out_button.config(state=tk.DISABLED)
            self.test_speaker_button.config(state=tk.DISABLED)
            self.update_status("🚀 Starting...")
            
            try:
                self.translator.start(
                    self.source_lang_var.get(),
                    self.target_lang_var.get(),
                    voice_to_meeting,
                    voice_to_you,
                    self.update_status,
                    self.audio_level_callback
                )
            except Exception as e:
                self.is_running = False
                self.start_button.config(text="🟢 Start Translation", bg="#27AE60")
                self.test_vb_out_button.config(state=tk.NORMAL)
                self.test_speaker_button.config(state=tk.NORMAL)
                messagebox.showerror("Start Failed", str(e))
        else:
            self.is_running = False
            self.translator.stop()
            self.start_button.config(text="🟢 Start Translation", bg="#27AE60")
            self.test_vb_out_button.config(state=tk.NORMAL)
            self.test_speaker_button.config(state=tk.NORMAL)
            self.update_status("ℹ️ Stopped")
            self.progress.stop()
            self.mic_level_bar.config(value=0)
            self.meeting_level_bar.config(value=0)
    
    def clear_display(self):
        """Clear log"""
        self.translation_text.delete(1.0, tk.END)
        self.update_status("Log cleared")
    
    def on_closing(self):
        """Cleanup"""
        if self.is_running:
            self.translator.stop()
        self.translator.cleanup()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
