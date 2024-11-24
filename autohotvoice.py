import os
import time
from typing import Callable, Dict, Any
import google.generativeai as genai
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
import keyboard
from dotenv import load_dotenv
import json

load_dotenv()


class SpeechToFile:
    """
    A class for recording live speech, transcribing it using Deepgram API,
    and saving the final transcriptions to a file. After transcription,
    the text is analyzed using Gemini to check if any hooks are invoked,
    and if so, the corresponding callbacks are executed.
    """

    def __init__(self, api_key, output_file="transcriptions.txt"):
        """
        Initializes the SpeechToFile object.

        Args:
            api_key (str): The API key for the Deepgram service.
            output_file (str): The file where transcriptions will be saved.
        """
        self.api_key = api_key
        self.output_file = output_file
        self.mid_sentences = []  # Temporarily stores mid-sentences
        self.sentences = []  # Finalized sentences after transcription
        self.deepgram = DeepgramClient(api_key)  # Initialize Deepgram client
        self.dg_connection = None  # WebSocket connection for Deepgram
        self.microphone = None  # Microphone object
        self.is_recording = False  # Tracks recording state
        self.hooks: Dict[str, Dict[str, Any]] = {}  # Stores hooks with task, description, and callback

    def validate_hook_name(self, name: str):
        """Validates the hook name format."""
        if not name.isupper() or not all(c.isalnum() or c == "_" for c in name):
            raise ValueError("Hook name must be in uppercase letters and can only contain underscores.")

    def setup_callbacks(self):
        """
        Configures the event handlers for the WebSocket connection.
        """
        self.dg_connection.on(
            LiveTranscriptionEvents.Open,
            lambda ot_self, *args, **kwargs: self.on_open(*args, **kwargs),
        )
        self.dg_connection.on(
            LiveTranscriptionEvents.Transcript,
            lambda ot_self, *args, **kwargs: self.on_message(*args, **kwargs),
        )
        self.dg_connection.on(
            LiveTranscriptionEvents.Close,
            lambda ot_self, *args, **kwargs: self.on_close(*args, **kwargs),
        )
        self.dg_connection.on(
            LiveTranscriptionEvents.Error,
            lambda ot_self, *args, **kwargs: self.on_error(*args, **kwargs),
        )

    def on_open(self, open, **kwargs):
        """Event handler for when the WebSocket connection opens."""
        print("Connection Open")

    def on_close(self, close, **kwargs):
        """Event handler for when the WebSocket connection closes."""
        print("Connection Closed")

    def on_message(self, result, **kwargs):
        """
        Event handler for receiving a transcription message.
        Processes intermediate and final transcriptions.
        """
        sentence = result.channel.alternatives[0].transcript
        print(sentence)
        if len(sentence) == 0:
            return  # Ignore empty transcriptions

        if result.is_final:
            self.mid_sentences.append(sentence)

            if result.speech_final:
                utterance = " ".join(self.mid_sentences)
                print(f"Final Utterance: {utterance}")
                self.write_to_file(utterance)
                self.mid_sentences = []  # Clear buffer
                self.sentences.append(utterance)

    def on_error(self, error, **kwargs):
        """Event handler for when an error occurs in the WebSocket."""
        print(f"Error: {error}")

    def write_to_file(self, text):
        """
        Appends the given text to the output file.
        """
        with open(self.output_file, "a") as f:
            f.write(text + "\n")  # Add a newline after each transcription

    def add_hook(self, name: str, task: str, description: str, callback: Callable[[str], Any], schema: dict = None):
        """
        Adds a hook to be executed based on Gemini's response.

        Args:
            name (str): The name of the hook (must be in uppercase with underscores).
            task (str): The task to check with Gemini.
            description (str): A detailed description of the hook.
            callback (Callable): The function to execute if the task is invoked.
            schema (dict, optional): An OpenAPI schema defining the expected Gemini response format.
        """
        self.validate_hook_name(name)
        self.hooks[name] = {
            "task": task,
            "description": description,
            "callback": callback,
            "schema": schema or {},  # Use an empty schema if none is provided
        }

    def invoke_gemini(self, transcription: str):
        """
        Sends the transcription to Gemini and evaluates hooks.

        Args:
            transcription (str): The final transcription text.
        """
        if not self.hooks:
            print("No hooks registered.")
            return

        # Define the main schema for Gemini
        schema_properties = {}

        for name, hook_data in self.hooks.items():
            schema_properties[name] = {
                "type": "object",
                "properties": {
                    "invoked": {
                        "type": "boolean",
                        "description": hook_data["description"],
                    },
                    **hook_data["schema"],  # Incorporate additional schema
                },
                "required": ["invoked"],
            }

        schema = {
            "description": "Hook invocation status and response formats.",
            "type": "object",
            "properties": schema_properties,
            "required": list(self.hooks.keys()),
        }

        try:
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            response = model.generate_content(
                f"Determine which of the following hooks were invoked in this transcription: {transcription}.",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )

            print(transcription)
            print(f"Gemini Response: {response}")
            for hook_name, hook_result in json.loads(response.text).items():
                if hook_result["invoked"]:
                    print(f"Hook '{hook_name}' was invoked. Executing callback.")
                    self.hooks[hook_name]["callback"](transcription)
                else:
                    print(f"Hook '{hook_name}' was not invoked.")
        except Exception as e:
            print(f"Error invoking Gemini: {e}")

    def start(self):
        """
        Starts the speech recording and transcription process.
        """
        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=300,
        )

        print("\n\nPress Enter to exit...\n\n")

        try:
            while True:
                if keyboard.is_pressed("right shift"):
                    if not self.is_recording:
                        print("Right Shift pressed. Starting recording...")
                        self.dg_connection = self.deepgram.listen.websocket.v("1")
                        self.setup_callbacks()
                        if not self.dg_connection.start(options, addons={"no_delay": "true"}):
                            print("Failed to connect to Deepgram")
                            return
                        self.microphone = Microphone(self.dg_connection.send)
                        self.microphone.start()
                        self.is_recording = True
                        self.sentences = []
                        self.mid_sentences = []
                        print("Recording started.")
                else:
                    if self.is_recording:
                        print("Right Shift released. Stopping recording...")
                        self.microphone.finish()
                        self.dg_connection.finish()
                        self.microphone = None
                        self.dg_connection = None
                        self.is_recording = False
                        final_transcription = " ".join(self.sentences)
                        self.invoke_gemini(final_transcription)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting...")
            if self.microphone:
                self.microphone.finish()
            if self.dg_connection:
                self.dg_connection.finish()


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Configure Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    genai.configure(api_key=GEMINI_API_KEY)

    # Configure Deepgram API
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    if not DEEPGRAM_API_KEY:
        raise ValueError("DEEPGRAM_API_KEY is not set in the environment.")

    # Initialize the SpeechToFile class
    speech_recorder = SpeechToFile(api_key=DEEPGRAM_API_KEY, output_file="speech_log.txt")

    # Register hooks with custom schemas
    speech_recorder.add_hook(
        "INSERT_TEXT",
        task="check ingredients in transcription",
        description="Does the text ask for any text to be added or inserted?",
        callback=lambda text: print(f"Callback executed for INSERT_TEXT with transcription: {text}"),
        schema={
            "inserted_text": {
                "type": "string",
                "description": "The text to be inserted, if specified.",
            }
        },
    )

    speech_recorder.add_hook(
        "CHECK_FOR_ACTION",
        task="identify user intent for a specific action",
        description="Detects if the user asks for a specific action to be performed.",
        callback=lambda text: print(f"Callback executed for CHECK_FOR_ACTION with transcription: {text}"),
        schema={
            "action": {
                "type": "string",
                "description": "The action the user intends to perform.",
            }
        },
    )

    # Start the speech recording process
    print("Starting Speech-to-File system. Press 'Right Shift' to start recording, and release to stop.")
    speech_recorder.start()