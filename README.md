<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/readme_image_dark.png">
    <source media="(prefers-color-scheme: light)" srcset="static/readme_image.png">
    <img alt="A person singing in a microphone" src="static/readme_image.png" width="200" height="200" style="max-width: 100%;">
  </picture>
</p>

# AutoHotVoice 🎙️

Automate Your Computer Using Voice Commands

[![Beta Release](https://img.shields.io/badge/release-alpha-redπ)](#)
[![License: MIT](https://img.shields.io/github/license/river-berlin/AutoHotVoice)](https://github.com/river-berlin/AutoHotVoice/blob/main/LICENSE)

Note : This project is in the Alpha stage


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
   sudo python main.py
   ```

2. Press the Shift key to enable voice commands.
3. Speak your command to control your computer.

### Code Usage Example

The following example demonstrates how to set up and use AutoHotVoice with custom hooks for specific tasks:

```python
from src.autohotvoice import AutoHotVoice
from dotenv import load_dotenv
import os
import google.generativeai as genai
import pyautogui

# Load environment variables
load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"]) #setup gemini

autohotvoice = AutoHotVoice(api_key=os.environ["DEEPGRAM_API_KEY"], output_file="speech_log.txt")

def insert_text_callback(hook_result):
    print(f"Callback executed for INSERT_TEXT with transcription: {hook_result['inserted_text']}")
    pyautogui.typewrite(hook_result["inserted_text"])

autohotvoice.add_hook(
    "INSERT_TEXT",
    task="check ingredients in transcription",
    description="Does the text ask for any text to be added or inserted? Call this if the user says write something, or insert this text.",
    callback=insert_text_callback,
    schema={
        "inserted_text": {
            "type": "string",
            "description": "The text to be inserted, if specified.",
        }
    },
)

# Start the speech recording process
print("Starting AutoHotVoice system. Press 'Right Shift' to start recording, and release to stop.")
autohotvoice.start()
```

---
Happy Automating! 🎉
