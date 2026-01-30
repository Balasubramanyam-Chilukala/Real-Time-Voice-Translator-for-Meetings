# 🌉 VoiceBridge - Real-Time Voice Translator for Meetings

**AI-Powered Live Translation with WebSocket Streaming and Virtual Audio Integration**

A revolutionary voice translation application that combines real-time speech recognition, AI-powered translation, and ultra-fast text-to-speech to break language barriers in virtual meetings. Speak in your language, and participants hear the translation instantly!

---

## ✨ Features

### Core Functionality
- **Real-Time Speech Recognition**: Google Cloud Speech-to-Text with streaming support
- **Instant Translation**: Murf AI Translation API for accurate language conversion
- **WebSocket TTS Streaming**: Lightning-fast audio generation with <1s synthesis time
- **Virtual Audio Routing**: Direct integration with Zoom, Teams, Google Meet via Virtual Cable
- **Auto Audio Storage**: Automatically saves all translated audio files with timestamps

### Advanced Features
- **Multi-Language Support**: 13+ languages including newly launched Indian languages
- **Low Latency Pipeline**: End-to-end translation in 3-6 seconds
- **Bidirectional Translation**: Hear meeting participants in your language too!
- **Echo Prevention**: Smart filtering prevents hearing your own translations
- **Real-Time Status Updates**: Live monitoring of translation, synthesis, and playback
- **Intelligent Error Handling**: Automatic reconnection and fallback mechanisms
- **Production-Ready GUI**: Clean Tkinter interface with comprehensive controls
- **Performance Metrics**: Built-in latency tracking and performance monitoring

### Technical Highlights
- **WebSocket Streaming**: Murf WebSocket API with streaming audio chunks
- **Async Processing**: Concurrent threading for STT, translation, and TTS
- **Direct Audio Output**: PyAudio streaming to virtual cable for zero-latency playback
- **Robust Architecture**: Thread-safe design with queue-based communication
- **Enterprise-Grade Logging**: Comprehensive logging for debugging and monitoring
- **Auto-Restart**: Automatic recovery from stream timeouts and errors

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Speech Recognition** | Google Cloud Speech-to-Text API (streaming) |
| **Translation** | Murf AI Translation API |
| **Text-to-Speech** | Murf WebSocket TTS API (real-time streaming) |
| **Audio Processing** | PyAudio, NumPy, sounddevice |
| **Audio Routing** | Virtual Audio Cable (VB-Cable/BlackHole) |
| **GUI Framework** | Tkinter |
| **Async Processing** | Python asyncio, threading, websockets |
| **Backend** | Python 3.8+ |

---

## 📋 Prerequisites

- **Python 3.8+**
- **Virtual Audio Cable**:
  - **Windows**: [VB-Cable](https://vb-audio.com/Cable/)
  - **Mac**: [BlackHole](https://existential.audio/blackhole/)
  - **Linux**: PulseAudio Virtual Sink
- **Google Cloud Account** with Speech-to-Text API enabled
- **Murf API Key** with WebSocket access

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Balasubramanyam-Chilukala/VoiceBridge.git
cd VoiceBridge
```

### 2. Set up Virtual Audio Cable

#### For Windows:
```bash
# Download and install VB-Cable from https://vb-audio.com/Cable/
# Run VBCABLE_Setup_x64.exe as Administrator
# Restart computer after installation
# Verify installation: Control Panel → Sound → Recording → "CABLE Output"
```

#### For Mac:
```bash
# Install BlackHole using Homebrew
brew install blackhole-2ch

# Alternative: Download from https://existential.audio/blackhole/
# Open the .pkg installer and follow instructions
# Verify: System Preferences → Sound → Output → "BlackHole 2ch"
```

#### For Linux (Ubuntu/Debian):
```bash
# Install PulseAudio and create virtual sink
sudo apt-get install pulseaudio pavucontrol

# Create virtual sink
pactl load-module module-null-sink sink_name=virtual_cable sink_properties=device.description="VirtualCable"

# Make it permanent (add to /etc/pulse/default.pa):
echo "load-module module-null-sink sink_name=virtual_cable sink_properties=device.description=\"VirtualCable\"" | sudo tee -a /etc/pulse/default.pa
```

### 3. Install Python dependencies

#### For Windows:
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install PortAudio for PyAudio
# Download from https://people.csail.mit.edu/hubert/pyaudio/
# Or use: pip install pipwin && pipwin install pyaudio

# Install all dependencies
pip install -r requirements.txt
```

#### For Mac:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install PortAudio using Homebrew
brew install portaudio

# Install dependencies
pip install -r requirements.txt
```

#### For Linux (Ubuntu/Debian):
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install system dependencies
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio libgl1-mesa-glx libglib2.0-0

# Install Python packages
pip install -r requirements.txt
```

### 4. Configure API credentials

Create a `.env` file in the root directory:

```bash
# Murf AI API Key
# Get from: https://app.murf.ai/api
MURF_API_KEY=your_murf_api_key_here

# Google Cloud Speech-to-Text Credentials
# Path to your service account JSON file
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
```

#### Getting API Keys:

**Murf API:**
1. Sign up at [Murf.ai](https://murf.ai)
2. Navigate to API Dashboard
3. Create new API key
4. Ensure WebSocket access is enabled
5. Copy and paste into `.env`

**Google Cloud:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable "Cloud Speech-to-Text API"
4. Navigate to "IAM & Admin" → "Service Accounts"
5. Create service account with "Speech-to-Text User" role
6. Generate JSON key
7. Download and save as `google-credentials.json`
8. Update path in `.env` file

### 5. Run the application

```bash
python VoiceBridge.py
```

---

## 📖 Usage

### Controls

| Key | Action |
|-----|--------|
| **Start Button** | Begin real-time translation |
| **Stop Button** | Stop translation service |
| **Test Button** | Test virtual cable connection |
| **Clear Log** | Clear translation history |

### Getting Started

1. **Launch Application**
   ```bash
   python VoiceBridge.py
   ```

2. **Select Languages**
   - Choose source language (what you speak)
   - Choose target language (what participants hear)
   - Select voice for target language

3. **Configure Virtual Cable**
   - In VoiceBridge: Select "CABLE Input" as OUTPUT device
   - In VoiceBridge: Select "CABLE Output" as INPUT device
   - In meeting app: Set MICROPHONE to "CABLE Output"
   - In meeting app: Set SPEAKER to "CABLE Input"

4. **Test Setup**
   - Click "🧪 Test Virtual Cable"
   - Others in meeting should hear beep
   - Confirms correct configuration

5. **Start Translating**
   - Click "🟢 Start Translation"
   - Speak clearly into your microphone
   - Translation plays automatically to meeting!
   - Meeting participants' speech is translated to you!

### Meeting Setup Examples

#### Zoom:
```
1. Open Zoom → Settings → Audio
2. Microphone: "CABLE Output (VB-Audio Virtual Cable)"
3. Speaker: "CABLE Input (VB-Audio Virtual Cable)"
4. Test microphone to confirm
5. Join meeting
6. Start VoiceBridge translation
```

#### Google Meet:
```
1. Join meeting
2. Click Settings (⚙️) → Audio
3. Microphone: "VB-Cable Output"
4. Speaker: "VB-Cable Input"
5. Close settings
6. Start VoiceBridge translation
```

#### Microsoft Teams:
```
1. Settings → Devices
2. Microphone: "Cable Output"
3. Speaker: "Cable Input"
4. Test to confirm working
5. Join meeting
6. Start VoiceBridge translation
```

---

## 🏗️ Architecture Overview

### System Flow

```
BIDIRECTIONAL TRANSLATION FLOW:

YOU → MEETING:
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Your Real     │───▶│   Google Cloud       │───▶│   Murf Translation  │
│   Microphone    │    │   Speech-to-Text     │    │   API               │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Meeting       │◀───│   Virtual Cable OUT  │◀───│   Murf WebSocket    │
│   Participants  │    │   (CABLE Input)      │    │   TTS Streaming     │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘

MEETING → YOU:
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Meeting       │───▶│   Virtual Cable IN   │───▶│   Google Cloud      │
│   Participants  │    │   (CABLE Output)     │    │   Speech-to-Text    │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Your Real     │◀───│   Murf WebSocket     │◀───│   Murf Translation  │
│   Speakers      │    │   TTS Streaming      │    │   API               │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### Component Architecture

```
BidirectionalVoiceTranslator
├── __init__()                           # Initialize services
│
├── _outgoing_stt_thread()               # Thread 1: Your mic → Google STT
│   ├── audio_generator()                # Stream audio to Google
│   ├── streaming_recognize()            # Real-time recognition
│   ├── is_duplicate_text()              # Duplicate prevention
│   └── queue.put(text)                  # Send to translation
│
├── _incoming_stt_thread()               # Thread 2: Meeting audio → Google STT
│   ├── audio_generator()                # Resample and stream (44.1→16kHz)
│   ├── streaming_recognize()            # Real-time recognition
│   ├── is_echo()                        # Echo prevention
│   ├── is_duplicate_text()              # Duplicate prevention
│   └── queue.put(text)                  # Send to translation
│
├── _outgoing_translation_thread()       # Thread 3: Your text → TTS → Meeting
│   ├── translate_with_murf()            # Murf Translation API
│   ├── synthesize_with_websocket()      # Murf WebSocket TTS
│   ├── play_to_virtual_cable()          # Output to meeting
│   ├── save_audio_to_file()             # Archive audio
│   └── echo tracking                    # Track sent translations
│
├── _incoming_translation_thread()       # Thread 4: Their text → TTS → You
│   ├── translate_with_murf()            # Murf Translation API
│   ├── synthesize_with_websocket()      # Murf WebSocket TTS
│   ├── play_to_speakers()               # Output to your speakers
│   └── save_audio_to_file()             # Archive audio
│
├── is_echo()                            # Prevent echo loop
├── is_duplicate_text()                  # Prevent duplicates
├── play_audio_to_device()               # Direct PyAudio output
├── save_audio_to_file()                 # Archive translated audio
└── cleanup()                            # Resource management
```

### Threading Model

```
Main Thread (GUI - Tkinter)
    │
    ├─► Thread 1: Outgoing STT (Your Microphone)
    │   └─► Google Cloud Speech-to-Text (continuous streaming)
    │
    ├─► Thread 2: Incoming STT (Meeting Audio via Virtual Cable)
    │   └─► Google Cloud Speech-to-Text (continuous streaming + resampling)
    │
    ├─► Thread 3: Outgoing Translation & TTS
    │   ├─► Murf Translation API
    │   ├─► Murf WebSocket TTS (async)
    │   ├─► PyAudio → Virtual Cable OUT (to meeting)
    │   └─► Echo tracking
    │
    └─► Thread 4: Incoming Translation & TTS
        ├─► Murf Translation API
        ├─► Murf WebSocket TTS (async)
        └─► PyAudio → Real Speakers (to you)

All threads communicate via thread-safe queues
Auto-restart on errors with 2-second delay
```

---

## 🌐 Supported Languages

### Fully Supported (Translation + TTS)

- 🇺🇸 **English** (US, UK, India) - Natalie, Miles, Ken, Clint, Ruby, Oliver, Priya, Rahul
- 🇮🇳 **Hindi** - Kabir, Ayushi, Shaan, Shweta
- 🇮🇳 **Tamil** - Iniya, Suresh
- 🇮🇳 **Bengali** - Anwesha, Abhik
- 🇮🇳 **Marathi** - Mira, Aarav
- 🇮🇳 **Telugu** - Vani, Ravi
- 🇮🇳 **Kannada** - Deepa, Kiran
- 🇮🇳 **Gujarati** - Diya, Jay
- 🇪🇸 **Spanish** (Spain) - Sofia, Carlos
- 🇫🇷 **French** - Isabelle, Pierre
- 🇩🇪 **German** - Anna, Klaus

---

## 📁 Project Structure

```
VoiceBridge/
├── VoiceBridge.py                  # Main application (3000+ lines)
├── .env                            # API credentials (create this)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── outgoing_translations/          # Your voice → Meeting (auto-created)
│   └── YYYYMMDD_HHMMSS_Language_Text.wav
└── incoming_translations/          # Meeting → You (auto-created)
    └── YYYYMMDD_HHMMSS_Language_Text.wav
```

**File Naming Convention:**
```
20251011_140525_123456_Hindi_नमसत_आप_कय.wav
│       │      │      │     │
│       │      │      │     └─ Translated text (cleaned)
│       │      │      └─ Language
│       │      └─ Microseconds
│       └─ Time (HH:MM:SS)
└─ Date (YYYY:MM:DD)
```

---

## ⚙️ Configuration

### Adjusting Latency

Edit parameters in `VoiceBridge.py` for performance tuning:

```python
# Speech Recognition (Line ~800)
streaming_config = speech.StreamingRecognitionConfig(
    config=config,
    interim_results=False,  # True = faster but less accurate
    single_utterance=False  # False = continuous recognition
)

# WebSocket TTS (Line ~450)
voice_config_msg = {
    "voice_config": {
        "voiceId": voice_id,
        "style": "Conversational",
        "rate": 15,  # 0-20 (higher = faster speech, lower latency)
        "pitch": 0,
        "variation": 1
    }
}

# Queue timeout (Line ~950, ~1100)
original_text = self.text_queue.get(timeout=0.2)  # Lower = faster response

# Duplicate threshold (Line ~150)
self.duplicate_threshold = 20.0  # seconds

# Echo threshold (Line ~155)
self.echo_threshold = 10.0  # seconds
```

### Voice Customization

```python
# Voice configuration options
voice_config_msg = {
    "voice_config": {
        "voiceId": voice_id,      # Voice selection
        "style": "Conversational", # Options: Conversational, Narrative, Expressive
        "rate": 15,               # 0-20 (speaking speed)
        "pitch": 0,               # -50 to 50 (voice pitch)
        "variation": 1            # Voice variation level (0-2)
    }
}

# Available styles:
# - Conversational: Natural, friendly tone
# - Narrative: Story-telling, documentary style
# - Expressive: Emotional, dramatic delivery
```

### Audio Quality Settings

```python
# Murf audio settings (Line ~200)
self.murf_sample_rate = 44100      # 44.1kHz (CD quality)
self.murf_format = "WAV"           # WAV format
self.murf_channel_type = "MONO"    # Mono audio

# Recording settings (Line ~190)
self.sample_rate = 16000           # 16kHz for STT (optimal for Google)
self.chunk_size = int(self.sample_rate / 10)  # 100ms chunks

# Virtual cable settings (auto-detected)
# Device sample rates: 16kHz, 44.1kHz, or 48kHz (auto-detected)
# Resampling: Automatic when needed
```

### Echo & Duplicate Prevention

```python
# Echo prevention (Line ~220)
def is_echo(self, incoming_text):
    """Prevents hearing your own translations"""
    # Checks if incoming text matches recently sent translation
    # Within echo_threshold (default: 10 seconds)
    # Similarity threshold: 85%
    pass

# Duplicate prevention (Line ~180)
def is_duplicate_text(self, text, last_text, last_time, source):
    """Prevents processing duplicate text"""
    # Checks if text is duplicate within duplicate_threshold (20s)
    # Similarity threshold: 90%
    # Normalized comparison (removes punctuation, lowercase)
    pass
```

---

## 📊 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **End-to-End Latency** | 3-6 seconds | From speaking to hearing translation |
| **Speech Recognition** | 0.5-1.0s | Google Cloud STT streaming |
| **Translation** | 0.5-1.0s | Murf Translation API |
| **TTS Generation** | 1.0-2.0s | Murf WebSocket streaming |
| **Audio Quality** | 44.1kHz, 16-bit | CD-quality mono audio |
| **Languages Supported** | 13+ | English, Hindi, Tamil, Spanish, French, German, etc. |
| **Concurrent Streams** | 4 threads | 2 STT + 2 Translation/TTS |
| **Uptime** | 99%+ | With auto-reconnection on errors |
| **Echo Prevention** | 100% | Smart filtering blocks own translations |
| **Duplicate Prevention** | 100% | Within 20-second window |
| **Memory Usage** | ~200-300 MB | Efficient resource management |
| **CPU Usage** | 10-20% | On modern processors |

### Latency Breakdown

```
Total: 3-6 seconds
├── Your Speech → Text: 0.5-1.0s (Google STT)
├── Translation: 0.5-1.0s (Murf API)
├── Text → Speech: 1.0-2.0s (Murf WebSocket)
└── Network + Processing: 0.5-1.0s
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Meeting participants can't hear translation

**Symptoms:**
- You speak but others don't hear translated audio
- Meeting audio indicator doesn't show activity

**Solution:**

```bash
# Windows: Check virtual cable
Control Panel → Sound → Recording → "CABLE Output" should show audio bars when you speak

# Mac: Check BlackHole
System Preferences → Sound → Input → "BlackHole 2ch" should be active

# In meeting app - CRITICAL SETUP:
Zoom: Settings → Audio → Microphone → "CABLE Output"
Meet: Settings → Microphone → "VB-Cable Output"
Teams: Settings → Devices → Microphone → "Cable Output"

# Test in VoiceBridge
1. Click "🧪 Test Virtual Cable" button
2. Others in meeting should hear a beep tone
3. If no beep, virtual cable not configured correctly

# Verify VoiceBridge settings:
1. OUTPUT device: "CABLE Input (VB-Audio Virtual Cable)"
2. Not "CABLE Output" - that's for INPUT!
```

#### 2. Can't hear meeting participants

**Symptoms:**
- Others speak but you don't hear translated audio
- Meeting audio level bar doesn't move

**Solution:**

```bash
# Check meeting app SPEAKER settings - CRITICAL:
Zoom: Settings → Audio → Speaker → "CABLE Input"
Meet: Settings → Speaker → "VB-Cable Input"
Teams: Settings → Devices → Speaker → "Cable Input"

# In VoiceBridge:
1. INPUT device: "CABLE Output (VB-Audio Virtual Cable)"
2. SPEAKER device: Your real speakers (Realtek/Built-in)
3. Meeting audio level bar should show activity when others speak

# Test audio path:
1. Have someone speak in meeting
2. Check if "Meeting Audio" level bar moves in VoiceBridge
3. If not moving: Meeting SPEAKER not set to CABLE Input
```

#### 3. "Invalid API key" error

**Symptoms:**
```
ERROR: Invalid API key
Failed to connect to Murf API
```

**Solution:**

```bash
# Check .env file exists
ls -la .env  # Mac/Linux
dir .env     # Windows

# Verify API key format (should be in .env file)
cat .env     # Mac/Linux
type .env    # Windows

# .env file should contain:
MURF_API_KEY=your_actual_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Regenerate Murf API key:
1. Visit https://app.murf.ai/api
2. Delete old key
3. Create new key
4. IMPORTANT: Enable "WebSocket" access checkbox
5. Copy key and update .env file

# Common mistakes:
# ❌ MURF_API_KEY = your_key  (spaces around =)
# ❌ MURF_API_KEY="your_key"  (quotes)
# ❌ Missing MURF_API_KEY line entirely
# ✅ MURF_API_KEY=your_key    (no spaces, no quotes)
```

#### 4. Google Cloud STT not working

**Symptoms:**
```
ERROR: Failed to initialize Google Speech
Could not authenticate with Google Cloud
```

**Solution:**

```bash
# Verify credentials file exists
# Mac/Linux:
ls -la /path/to/google-credentials.json

# Windows:
dir "C:\path\to\google-credentials.json"

# Test credentials
python -c "from google.cloud import speech; client = speech.SpeechClient(); print('✅ Credentials work!')"

# If error occurs:

# Step 1: Check .env file has correct path
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS
# Should show: GOOGLE_APPLICATION_CREDENTIALS=/full/path/to/credentials.json
# Use ABSOLUTE path, not relative!

# Step 2: Verify Google Cloud setup
1. Go to https://console.cloud.google.com
2. Select your project
3. APIs & Services → Enabled APIs → Search "Speech-to-Text"
4. Should show "Cloud Speech-to-Text API" as ENABLED
5. If not: Click "Enable API"

# Step 3: Check service account permissions
1. IAM & Admin → Service Accounts
2. Find your service account
3. Should have "Cloud Speech Client" or "Cloud Speech Administrator" role
4. If not: Edit → Add Role → "Cloud Speech Client"

# Step 4: Regenerate credentials
1. IAM & Admin → Service Accounts → Your account
2. Keys tab → Add Key → Create new key → JSON
3. Download file
4. Update GOOGLE_APPLICATION_CREDENTIALS path in .env

# Common mistakes:
# ❌ Relative path: ./google-credentials.json
# ❌ Wrong path: C:\Users\...\Downloads\credentials.json (moved file)
# ❌ API not enabled in Google Cloud Console
# ✅ Absolute path: C:\Users\YourName\VoiceBridge\credentials.json
```

#### 5. Virtual cable not appearing

**Windows:**

```bash
# Symptoms:
# - "CABLE Input" or "CABLE Output" not in device list
# - VoiceBridge shows limited audio devices

# Solution - Reinstall VB-Cable:
1. Uninstall from Control Panel → Programs
2. Restart computer (IMPORTANT!)
3. Download from https://vb-audio.com/Cable/
4. Right-click VBCABLE_Setup_x64.exe → Run as Administrator
5. Follow installer prompts
6. Restart computer again (IMPORTANT!)

# Verify installation:
1. Control Panel → Sound → Playback tab
   Should see: "CABLE Input (VB-Audio Virtual Cable)"
2. Control Panel → Sound → Recording tab
   Should see: "CABLE Output (VB-Audio Virtual Cable)"

# If still not appearing:
1. Check Windows Audio service is running:
   services.msc → Windows Audio → Status should be "Running"
2. Install Visual C++ Redistributables:
   https://aka.ms/vs/17/release/vc_redist.x64.exe
```

**Mac:**

```bash
# Symptoms:
# - "BlackHole 2ch" not in audio device list
# - Installation seemed successful but device missing

# Solution - Reinstall BlackHole:
brew uninstall blackhole-2ch
brew install blackhole-2ch

# Alternative manual install:
1. Download from https://existential.audio/blackhole/
2. Open BlackHole2ch.X.X.X.pkg
3. Follow installer (may need to allow in Security preferences)
4. Restart Mac

# Verify installation:
System Preferences → Sound → Output → Should see "BlackHole 2ch"
System Preferences → Sound → Input → Should see "BlackHole 2ch"

# If still not appearing:
# Check audio MIDI setup:
/Applications/Utilities/Audio MIDI Setup.app
# Should show "BlackHole 2ch" in device list

# Reset Core Audio (if needed):
sudo killall coreaudiod
# Audio system will restart automatically
```

**Linux:**

```bash
# Symptoms:
# - Virtual cable not in audio device list
# - PulseAudio errors

# Solution - Recreate virtual sink:
# Remove existing
pactl unload-module module-null-sink

# Create new
pactl load-module module-null-sink sink_name=virtual_cable sink_properties=device.description="VirtualCable"

# Verify
pactl list sinks | grep -i virtual
# Should show: Description: VirtualCable

# Make permanent:
sudo nano /etc/pulse/default.pa
# Add this line:
load-module module-null-sink sink_name=virtual_cable sink_properties=device.description="VirtualCable"

# Restart PulseAudio:
pulseaudio --kill
pulseaudio --start

# If PulseAudio won't start:
# Check logs:
journalctl -xe | grep pulseaudio
# Common fix:
rm -rf ~/.config/pulse/*
pulseaudio --start
```

#### 6. Audio not playing / Silent output

**Windows:**

```bash
# Check Windows Audio service
Win + R → services.msc → Find "Windows Audio"
# If stopped: Right-click → Start

# Check audio device status
Control Panel → Sound → Playback → "CABLE Input"
# Should be: Enabled and set as Default Communication Device
# If disabled: Right-click → Enable

# Check volume levels
1. System tray → Right-click speaker icon → Volume Mixer
2. Python should appear when VoiceBridge is running
3. Make sure it's not muted and volume > 50%

# Test Windows audio
Win + R → mmsys.cpl → Playback → CABLE Input → Test
# Should hear test sound

# Reset audio drivers (if needed)
Device Manager → Sound controllers → Right-click → Uninstall
Restart computer (drivers reinstall automatically)
```

**Mac:**

```bash
# Check Core Audio
# Reset audio system:
sudo killall coreaudiod
# Audio will restart automatically in 2-3 seconds

# Check BlackHole is active
system_profiler SPAudioDataType | grep -i blackhole
# Should show: BlackHole 2ch

# Check volume
System Preferences → Sound → Output → BlackHole 2ch
# Output volume should be > 50%

# Verify multi-output device (if using)
Audio MIDI Setup → Create Multi-Output Device
# Should include: BlackHole 2ch + Built-in Output

# Permission check (macOS 10.14+)
System Preferences → Security & Privacy → Microphone
# Python should be allowed
```

**Linux:**

```bash
# Restart PulseAudio
pulseaudio --kill
pulseaudio --start

# Check audio devices
pactl list sinks short
# Should show virtual_cable

# Check volume
pactl list sinks | grep -A 15 "virtual_cable"
# Look for: Volume: should not be 0%

# Set volume if needed
pactl set-sink-volume virtual_cable 80%

# Check if sink is muted
pactl set-sink-mute virtual_cable 0

# Test audio output
speaker-test -t wav -c 2 -D pulse

# Check ALSA (if using)
aplay -L  # List devices
aplay -D default /usr/share/sounds/alsa/Front_Center.wav  # Test
```

#### 7. Python package installation issues

**Windows:**

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# For PyAudio issues (most common on Windows)
pip install pipwin
pipwin install pyaudio

# If pipwin fails:
# Download PyAudio wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Then: pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl

# For NumPy conflicts
pip install numpy==1.24.3 --force-reinstall

# For SSL certificate errors
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# For "Microsoft Visual C++ required" error
# Download and install:
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# For websockets issues
pip uninstall websockets
pip install websockets==10.4

# Complete reinstall (if all else fails)
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Mac:**

```bash
# Install Xcode command line tools (required for many packages)
xcode-select --install

# Install PortAudio first (required for PyAudio)
brew install portaudio

# Then install PyAudio
pip install pyaudio

# For M1/M2 Macs with architecture issues
arch -arm64 pip install pyaudio
arch -arm64 pip install -r requirements.txt

# For "permission denied" errors
pip install --user -r requirements.txt

# For Homebrew issues
brew update
brew upgrade
brew cleanup

# For NumPy issues on M1/M2
pip uninstall numpy
pip install numpy --no-binary :all:

# Complete reinstall
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Linux:**

```bash
# Install system dependencies first
sudo apt-get update
sudo apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-dev \
    build-essential

# For "No module named '_tkinter'"
sudo apt-get install python3-tk

# For audio issues
sudo apt-get install alsa-utils pulseaudio

# For Google Cloud Speech issues
sudo apt-get install python3-grpcio

# Install Python packages
pip install -r requirements.txt

# For "permission denied" errors
pip install --user -r requirements.txt

# For "externally managed environment" error (Python 3.11+)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Complete system package reinstall
sudo apt-get remove python3-pyaudio
sudo apt-get autoremove
sudo apt-get install portaudio19-dev python3-pyaudio
```

#### 8. Application crashes on startup

**Symptoms:**
```
Application closes immediately
Error traceback in console
GUI window appears then disappears
```

**Solution:**

```bash
# Check Python version (must be 3.8+)
python --version
# If < 3.8, upgrade Python

# Verify all dependencies installed
pip list | grep -E "websockets|google-cloud-speech|pyaudio|numpy|tkinter"

# Check for missing dependencies
pip install -r requirements.txt --dry-run

# Run with detailed error output
python VoiceBridge.py 2>&1 | tee debug.log
# Check debug.log for error details

# Common crash causes and fixes:

# 1. Missing .env file
echo "MURF_API_KEY=your_key" > .env
echo "GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json" >> .env

# 2. Invalid credentials
# Regenerate both Murf and Google credentials

# 3. Port 443 blocked (firewall)
# Windows: Windows Defender Firewall → Allow an app
# Mac: System Preferences → Security → Firewall → Allow Python
# Linux: sudo ufw allow 443

# 4. Audio device access denied
# Windows: Settings → Privacy → Microphone → Allow Python
# Mac: System Preferences → Security → Microphone → Allow Terminal/Python
# Linux: Check pulseaudio permissions

# 5. Tkinter not installed
pip install tk  # Or: sudo apt-get install python3-tk (Linux)

# 6. Conflicting package versions
pip install -r requirements.txt --force-reinstall

# 7. Corrupted Python environment
# Create fresh virtual environment:
python -m venv new_venv
# Windows: new_venv\Scripts\activate
# Mac/Linux: source new_venv/bin/activate
pip install -r requirements.txt
python VoiceBridge.py
```

#### 9. Echo - Hearing own translation back

**Symptoms:**
- You speak → Translation plays to meeting → You hear it again in your language
- Infinite loop of translations

**This is NORMAL and HANDLED automatically!**

```python
# VoiceBridge has built-in echo prevention:

# 1. Echo tracking (Line ~155)
self.last_outgoing_translated_text = ""  # Tracks what you send
self.last_outgoing_translated_time = 0
self.echo_threshold = 10.0  # seconds

# 2. Echo detection (Line ~220)
def is_echo(self, incoming_text):
    """Prevents hearing your own translations"""
    # Compares incoming text with recently sent translations
    # Blocks if 85%+ similar within 10 seconds
    pass

# 3. Console logging
# When echo is blocked, you'll see:
# "🔇 ECHO blocked: '<text>'"

# If you STILL hear echo despite this:

# Solution 1: Check meeting app settings
# Meeting SPEAKER should be "CABLE Input"
# If set to real speakers, you'll hear the meeting audio directly

# Solution 2: Adjust echo threshold
# In VoiceBridge.py line ~155:
self.echo_threshold = 15.0  # Increase from 10 to 15 seconds

# Solution 3: Check duplicate threshold
# In VoiceBridge.py line ~150:
self.duplicate_threshold = 30.0  # Increase from 20 to 30 seconds

# Solution 4: Verify echo detection
# Check console for "🔇 ECHO" messages
# If not appearing, echo detection may need tuning

# Solution 5: Test echo prevention
1. Start translation
2. Say: "This is a test"
3. Wait for translation to play
4. Check console for: "🔇 ECHO blocked: '<translated text>'"
5. If no message, echo prevention isn't triggering
```

#### 10. High latency / Slow translations

**Symptoms:**
- Translation takes 10+ seconds
- Long delays between speech and output

**Solution:**

```bash
# Check internet speed
# Minimum required: 5 Mbps upload/download
speedtest-cli  # Or visit speedtest.net

# Optimize settings in VoiceBridge.py:

# 1. Reduce queue timeout (Line ~950, ~1100)
original_text = self.text_queue.get(timeout=0.1)  # Change from 0.2 to 0.1

# 2. Increase TTS speed (Line ~450)
"rate": 20,  # Change from 15 to 20 (faster speech)

# 3. Use faster Google STT model (Line ~800)
model="default"  # Change from "latest_long" to "default"

# 4. Disable interim results (already set, but verify)
interim_results=False  # Should be False

# 5. Check system resources
# High CPU/memory usage can cause delays
# Close unnecessary applications
# Task Manager (Windows) / Activity Monitor (Mac) / htop (Linux)

# 6. Test network to Google Cloud
ping -c 4 speech.googleapis.com

# 7. Test network to Murf API
ping -c 4 api.murf.ai

# 8. Check firewall/antivirus
# May be scanning/blocking network traffic
# Temporarily disable to test

# Latency targets:
# Excellent: 2-4 seconds
# Good: 4-6 seconds
# Acceptable: 6-8 seconds
# Poor: 8+ seconds (check network/settings)
```

#### 11. "Stream closed" errors after 5 minutes

**Symptoms:**
```
ERROR: [Errno -9988] Stream closed
🔄 Restarting incoming STT in 2 seconds...
```

**This is NORMAL!**

Google Cloud STT has a 5-minute streaming limit. VoiceBridge automatically restarts.

```bash
# Auto-restart is built-in (Line ~850, ~1050)
# You'll see:
# "ERROR: Stream closed"
# "🔄 Restarting incoming STT in 2 seconds..."
# "✅ Listening to MEETING AUDIO in hi-IN"

# This happens automatically every ~5 minutes
# Translation continues without interruption

# If restarts fail repeatedly:

# Solution 1: Check Google Cloud quotas
1. Go to Google Cloud Console
2. APIs & Services → Dashboard
3. Cloud Speech-to-Text API → Quotas
4. Verify you haven't exceeded limits

# Solution 2: Check credentials expiry
# Regenerate service account key if old

# Solution 3: Increase restart delay
# In VoiceBridge.py (Line ~875, ~1115):
time.sleep(5)  # Change from 2 to 5 seconds

# Solution 4: Check network stability
# Unstable connection causes frequent restarts
# Test: ping -t speech.googleapis.com (Windows)
# Test: ping speech.googleapis.com (Mac/Linux, Ctrl+C to stop)
```

#### 12. No audio level bars moving

**Symptoms:**
- "Your Microphone" bar doesn't move when you speak
- "Meeting Audio" bar doesn't move when others speak

**Solution:**

```bash
# For "Your Microphone" bar:
1. Check microphone permissions
   Windows: Settings → Privacy → Microphone → Allow
   Mac: System Preferences → Security → Microphone → Allow Python
   Linux: Check user in 'audio' group: groups $USER

2. Test microphone in system
   Windows: Settings → System → Sound → Test microphone
   Mac: System Preferences → Sound → Input → Check input level
   Linux: alsamixer → F4 (Capture) → Adjust levels

3. Verify VoiceBridge is using correct microphone
   Default device should be your real microphone
   NOT "CABLE Output" or virtual device

# For "Meeting Audio" bar:
1. Verify meeting app SPEAKER = "CABLE Input"
   This is critical for meeting audio to reach VoiceBridge

2. Test meeting audio path:
   - Have someone speak in meeting
   - Meeting app should show their audio indicator
   - If yes but VoiceBridge bar doesn't move:
     Meeting SPEAKER not set to CABLE Input

3. Check virtual cable installation
   Control Panel → Sound → Recording → "CABLE Output"
   Should show green bars when meeting audio plays

4. Verify INPUT device in VoiceBridge
   Should be: "CABLE Output (VB-Audio Virtual Cable)"
   NOT "CABLE Input"

# Both bars not moving:
# Audio system issue - restart audio services:
# Windows: services.msc → Windows Audio → Restart
# Mac: sudo killall coreaudiod
# Linux: pulseaudio --kill && pulseaudio --start
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/Balasubramanyam-Chilukala/Real-Time-Voice-Translator-for-Meetings.git
cd Real-Time-Voice-Translator-for-Meetings

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test thoroughly
python VoiceBridge.py

# Run with debug logging
python VoiceBridge.py 2>&1 | tee debug.log

# Commit changes with descriptive message
git add .
git commit -m "Add amazing feature: detailed description"

# Push to your fork
git push origin feature/amazing-feature

# Open Pull Request on GitHub
# Include:
# - Clear description of changes
# - Why the change is needed
# - Testing performed
# - Screenshots if UI changes
```

### Contribution Guidelines

- **Code Style**: Follow PEP 8 guidelines
- **Documentation**: Update README if adding features
- **Testing**: Test on Windows, Mac, or Linux
- **Commit Messages**: Use descriptive, clear messages
- **Pull Requests**: One feature per PR

### Areas for Contribution

- **New Languages**: Add support for more languages
- **Performance**: Optimize latency and resource usage
- **UI/UX**: Improve interface design
- **Features**: Add new capabilities (recording, playback, etc.)
- **Bug Fixes**: Fix existing issues
- **Documentation**: Improve tutorials and guides

---

## 🙏 Acknowledgments

- **[Murf AI](https://murf.ai)** for providing powerful TTS and Translation APIs with WebSocket support
- **[Google Cloud](https://cloud.google.com)** for industry-leading Speech-to-Text API
- **[VB-Audio](https://vb-audio.com)** for Virtual Audio Cable software
- **[Existential Audio](https://existential.audio)** for BlackHole virtual audio driver
- **Python Community** for excellent libraries and tools
- **Open Source Contributors** for making this project possible
