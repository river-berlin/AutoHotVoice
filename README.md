<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/readme_image_dark.png">
    <source media="(prefers-color-scheme: light)" srcset="static/readme_image.png">
    <img alt="A person singing in a microphone" src="static/readme_image.png" width="200" height="200" style="max-width: 100%;">
  </picture>
</p>

<p align="center">
  AutoHotVoice 🎙️  
  <br>
  Automate Your Computer Using Voice Commands
</p>

<p align="center">
    <a href="#"><img src="https://img.shields.io/badge/release-alpha-redπ" alt="Beta Release"></a>
    <a href="https://github.com/river-berlin/AutoHotVoice/blob/main/LICENSE"><img src="https://img.shields.io/github/license/river-berlin/AutoHotVoice" alt="License: MIT"></a>
</p>

---

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
