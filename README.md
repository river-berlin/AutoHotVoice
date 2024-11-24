# AutoHotVoice 🎙️
_Automate Your Computer Using Voice Commands_

<img src="static/README_image.jpg" alt="A person singing in a microphone" width="200" height="200">


## Overview

AutoHotVoice integrates **Google Gemini** and **DeepGram** to provide seamless voice-activated control and shortcuts for daily computer tasks.

### Key Features

- **Voice Control:** Execute commands with voice recognition using Google Gemini and DeepGram technologies.
- **Shortcut Activation:** Easily trigger the interface with the **Shift key**.
- **Fully Customizable:** Personalize your experience with a configurable Python file.

## Getting Started

### Prerequisites

- Python version 3.8 or newer
- Google Gemini API access
- DeepGram API access

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/river-berlin/AutoHotVoice
   ```

2. Install necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys in the `.env` file:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   DEEPGRAM_API_KEY=your_api_key_here
   ```

### Running the Application

1. Launch the script:
   ```bash
   sudo python autohotvoice.py
   ```

2. Press the Shift key to enable voice commands.
3. Speak your command to control your computer.

---
Happy Automating! 🎉
