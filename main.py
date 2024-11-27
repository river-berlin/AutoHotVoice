from src.autohotvoice.autohotvoice import AutoHotVoice
from dotenv import load_dotenv
import os
import google.generativeai as genai
import pyautogui
import pyperclip
import platform

# Load environment variables
load_dotenv()

# configure gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

autohotvoice = AutoHotVoice(
    f"You're a friendly chatbot, A user has asked you for stuff based on the following transcription, reply with what the user probably wants here, Thanks, appreciate youuuuu :), -- transcription :",
    api_key=os.environ["DEEPGRAM_API_KEY"], output_file="speech_log.txt"
)


# Define the callback function for text insertion
def insert_text_callback(hook_result):
    """
    Callback function to handle text insertion. Copies the text to the clipboard
    and pastes it using the appropriate key combination for the operating system.
    """
    # Get the inserted text
    inserted_text = hook_result["inserted_text"]

    # Copy the text to the clipboard
    pyperclip.copy(inserted_text)

    # Determine the user's operating system
    os_type = platform.system()

    # Determine the appropriate modifier key (Command for macOS, Control otherwise)
    if os_type == "Darwin":  # macOS
        modifier_key = "command"
    else:  # Windows or Linux
        modifier_key = "ctrl"

    # Use a context manager to hold the appropriate modifier key and press 'V' to paste
    with pyautogui.hold(modifier_key):
        pyautogui.press("v")

    # Log the action for debugging
    print(f"Text inserted using {modifier_key} + V: {inserted_text}")


# Define schema for hook
insert_text_schema = {
    "inserted_text": {
        "type": "string",
        "description": (
            "The text to be inserted or added should go here. Call this if the user says 'write something', "
            "or uses phrases like 'read me' (often misinterpreted by voice recognition as 'write me'). "
            "This should contain the specific text requested, such as a poem, an email, or any other "
            "formatted content the user needs."
            "So, if there is an email requested here, put the specific email inside here, if there is a poem, put that poem over here to be inserted"
        ),
    }
}

# Register hooks with custom schemas
autohotvoice.add_hook(
    name="INSERT_TEXT",
    task="check ingredients in transcription",
    description=(
        "Does the text ask for any text to be added or inserted? Call this if the user says 'write something'. "
        "Use this even if the user uses phrases like 'read me' that could mean 'write me'. (often misinterpreted by voice recognition)."
        "This should contain the specific text requested, such as a poem, an email, or any other "
        "the user needs."
        "So, if there is an email requested here, put specific email inside here, if there is a poem, put that poem over here to be inserted"
    ),
    callback=insert_text_callback,  # Callback function to handle the request
    schema=insert_text_schema,
)

# Start the speech recording process
print(
    "Starting AutoHotKey system. Press 'Right Shift' to start recording, and release to stop."
)
autohotvoice.start()
