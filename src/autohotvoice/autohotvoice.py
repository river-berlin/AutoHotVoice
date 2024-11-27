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
import pygame
import os


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

    def __init__(self, base_transcript: str, api_key, output_file="transcriptions.txt"):
        """
        Initializes the AutoHotVoice object.

        Args:
            base_transcript (str): The base transcript provided to AutoHotVoice
            api_key (str): The API key for the Deepgram service.
            output_file (str): The file where transcriptions will be saved.
        """
        self._base_transcript = base_transcript
        self.api_key = api_key
        self.output_file = output_file
        self.mid_sentences = []  # Temporarily stores mid-sentences
        self.sentences = []  # Finalized sentences after transcription
        self.deepgram = DeepgramClient(api_key)  # Initialize Deepgram client
        self.is_recording = False  # Tracks recording state
        self.hooks: Dict[str, Dict[str, Any]] = {}  # Stores hooks
        self.gemini_thingamie = GeminiThingamie(
            self.base_transcript
        )  # Initialize GeminiThingamie
        self.release_hooks = []
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    @property
    def base_transcript(self):
        return self._base_transcript

    @base_transcript.setter
    def base_transcript(self, value):
        self._base_transcript = value
        self.gemini_thingamie.base_transcript = value

    def validate_hook_name(self, name: str):
        """Validates the hook name format."""
        if not name.isupper() or not all(c.isalnum() or c == "_" for c in name):
            raise ValueError(
                "Hook name must be in uppercase letters and can only contain underscores."
            )

    def write_to_file(self, text):
        """Appends the given text to the output file."""
        with open(self.output_file, "a") as f:
            f.write(text + "\n")

    def add_hook(
        self,
        name: str,
        task: str,
        description: str,
        callback: Callable[[str], Any],
        schema: dict = None,
    ):
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

    def add_release_hook(self, callback):
        """Register a function to be called before the user starts speaking.

        This function is called every time the user releases the trigger button.

        Args:
            callback: The function to be called. It will be called with no arguments.
        """
        self.release_hooks.append(callback)

    def start(self):
        """
        Starts the speech recording and transcription process.
        """
        recorder = AudioRecorder(sample_rate=16000, channels=1)
        print("Press 'Right Shift' to start recording.")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        sounds_dir = os.path.join(base_dir, "sounds")

        sound1 = pygame.mixer.Sound(os.path.join(sounds_dir, "ping.mp3"))
        sound2 = pygame.mixer.Sound(os.path.join(sounds_dir, "ping-2.mp3"))

        while True:
            # Updated code snippet
            if keyboard.is_pressed("right shift"):

                if not self.is_recording:
                    self.is_recording = True
                    sound1.play()  # Play ping sound
                    recorder.start()
            else:
                if self.is_recording:
                    self.is_recording = False

                    # execute the release hooks
                    for hook in self.release_hooks:
                        hook()

                    sound2.play()  # Play ping-2 sound
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

                    final_transcription = response["results"]["channels"][0][
                        "alternatives"
                    ][0]["transcript"]

                    if final_transcription.strip():
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
        self.gemini_thingamie.set_base_transcript(self.base_transcript)
        self.gemini_thingamie.process_transcription(transcription, self.hooks)
