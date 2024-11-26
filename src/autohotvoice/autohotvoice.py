"""
AutoHotVoice Module
===================

This module provides functionality for recording speech, transcribing it using Deepgram's API, 
and processing transcription data with Gemini's AI for hook-based task execution.

Classes:
--------
- AutoHotVoice: A class for recording live speech, transcribing it using Deepgram API, and 
  invoking GeminiThingamie for hook-based task execution.
"""
import time
from typing import Callable, Dict, Any
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
import keyboard
import httpx
from datetime import datetime
from .audiorecorder import AudioRecorder
from .geminithingamie import GeminiThingamie


class AutoHotVoice:
    """
    A class for recording live speech, transcribing it using Deepgram API,
    and invoking GeminiThingamie for hook-based task execution.

    Attributes:
        api_key (str): The API key for the Deepgram service.
        output_file (str): The file where transcriptions will be saved.
        hooks (dict): A dictionary storing hooks for specific tasks.
        is_recording (bool): Tracks whether the recording is currently in progress.
        deepgram (DeepgramClient): The Deepgram client for transcription.
        gemini_thingamie (GeminiThingamie): The GeminiThingamie object for AI task execution.

    Example:
        The following example demonstrates how to configure and use the `AutoHotVoice` class:

        .. code-block:: python

            from autohotvoice import AutoHotVoice
            import os
            import pyautogui
            import google.generativeai as genai

            # Initialize the AutoHotVoice class with Deepgram API key
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            autohotvoice = AutoHotVoice(api_key=os.environ["DEEPGRAM_API_KEY"], output_file="speech_log.txt")

            # Define a callback function for text insertion
            def insert_text_callback(hook_result):
                pyautogui.typewrite(hook_result["inserted_text"])

            # Add hooks for specific tasks
            autohotvoice.add_hook(
                "INSERT_TEXT",
                task="check ingredients in transcription",
                description="Does the text ask for any text to be added or inserted? Call this if the user says 'write something' or 'insert this text' or something along those lines.",
                callback=insert_text_callback,  # Use the defined callback function
                schema={
                    "inserted_text": {
                        "type": "string",
                        "description": "The text to be inserted, if specified, keep this to what is likely needed and nothing more.",
                    }
                },
            )

            # Start the speech recording and transcription process
            autohotvoice.start()
    """

    def __init__(self, api_key, output_file="transcriptions.txt"):
        """
        Initializes the AutoHotVoice object.

        Args:
            api_key (str): The API key for the Deepgram service.
            output_file (str): The file where transcriptions will be saved.
        """
        self.api_key = api_key
        self.output_file = output_file
        self.mid_sentences = []  # Temporarily stores mid-sentences
        self.sentences = []  # Finalized sentences after transcription
        self.deepgram = DeepgramClient(api_key)  # Initialize Deepgram client
        self.is_recording = False  # Tracks recording state
        self.hooks: Dict[str, Dict[str, Any]] = {}  # Stores hooks
        self.gemini_thingamie = GeminiThingamie()  # Initialize GeminiThingamie

    def validate_hook_name(self, name: str):
        """Validates the hook name format."""
        if not name.isupper() or not all(c.isalnum() or c == "_" for c in name):
            raise ValueError("Hook name must be in uppercase letters and can only contain underscores.")

    def write_to_file(self, text):
        """Appends the given text to the output file."""
        with open(self.output_file, "a") as f:
            f.write(text + "\n")

    def add_hook(self, name: str, task: str, description: str, callback: Callable[[str], Any], schema: dict = None):
        """
        Adds a hook to be executed based on GeminiThingamie's response.

        Args:
            name (str): Hook name (must be uppercase with underscores).
            task (str): The task to check with GeminiThingamie.
            description (str): A detailed description of the hook.
            callback (Callable): The function to execute if the task is invoked.
            schema (dict, optional): Schema for GeminiThingamie's response.
        """
        self.validate_hook_name(name)
        self.hooks[name] = {
            "task": task,
            "description": description,
            "callback": callback,
            "schema": schema or {},
        }

    def start(self):
        """
        Starts the speech recording and transcription process.
        """
        recorder = AudioRecorder(sample_rate=16000, channels=1)
        print("Press 'Right Shift' to start recording.")

        while True:
            if keyboard.is_pressed("right shift"):
                if not self.is_recording:
                    self.is_recording = True
                    recorder.start()
            else:
                if self.is_recording:
                    self.is_recording = False
                    audio_buffer = recorder.stop()
                    recorder.save("test.wav")

                    options = PrerecordedOptions(
                        model="nova-2",
                        smart_format=True,
                        utterances=True,
                        punctuate=True,
                        diarize=True,
                    )

                    payload: FileSource = {"buffer": audio_buffer}

                    before = datetime.now()
                    response = self.deepgram.listen.rest.v("1").transcribe_file(
                        payload, options, timeout=httpx.Timeout(300.0, connect=10.0)
                    )
                    after = datetime.now()
                    print(f"Transcribed in {after - before}")

                    final_transcription = response["results"]["channels"][0]["alternatives"][0]["transcript"]
                    self.invoke_gemini(final_transcription)

            time.sleep(0.1)

    def invoke_gemini(self, transcription: str):
        """
        Sends the transcription to GeminiThingamie and evaluates hooks.

        Args:
            transcription (str): The final transcription text.
        """
        if not self.hooks:
            print("No hooks registered.")
            return

        self.write_to_file("Invoked with: " + transcription)
        self.gemini_thingamie.process_transcription(transcription, self.hooks)