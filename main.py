from src.autohotvoice.autohotvoice import AutoHotVoice
from dotenv import load_dotenv
import os
import google.generativeai as genai
import pyautogui

# Load environment variables
load_dotenv()

# configure gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

autohotvoice = AutoHotVoice(
    api_key=os.environ["DEEPGRAM_API_KEY"], output_file="speech_log.txt"
)


# Define the callback function for text insertion
def insert_text_callback(hook_result):
    # Log the text for debugging
    print(
        f"Callback executed for INSERT_TEXT with transcription: {hook_result["inserted_text"]}"
    )
    # Simulate typing the text using pyautogui
    pyautogui.typewrite(hook_result["inserted_text"])


# Register hooks with custom schemas
autohotvoice.add_hook(
    "INSERT_TEXT",
    task="check ingredients in transcription",
    description="Does the text ask for any text to be added or inserted?, call this if the user says write something, or insert this text or something on those lines",
    callback=insert_text_callback,  # Use the defined callback function
    schema={
        "inserted_text": {
            "type": "string",
            "description": "The text to be inserted, if specified, keep this to what is likely needed and nothing more.",
        }
    },
)

# Start the speech recording process
print(
    "Starting AutoHotKey system. Press 'Right Shift' to start recording, and release to stop."
)
autohotvoice.start()
