"""
audio_recorder.py

This module provides functionality for recording audio from a microphone using 
the `sounddevice` and `soundfile` libraries. The `AudioRecorder` class handles 
audio recording, storing frames, and exporting the audio to a file or as a 
bytes-like object.

Classes:
    - AudioRecorder: A class for managing microphone audio recording.
"""

import io
import sounddevice as sd
import soundfile as sf
import numpy as np


class AudioRecorder:
    """
    A class for recording audio from the microphone.

    This class uses the `sounddevice` library to capture audio input and the
    `soundfile` library to handle audio file creation. It supports saving
    audio data to a file or returning it as a bytes-like object.

    Attributes:
        sample_rate (int): The sample rate for audio recording.
        channels (int): Number of audio channels (1 for mono, 2 for stereo).
        stream (sounddevice.InputStream): The audio input stream.
        is_recording (bool): Indicates if the recording is in progress.
        audio_frames (list): List to store audio frames during recording.

    Example:
        The following example demonstrates how to use the `AudioRecorder` class
        to record and save audio to a file:

        .. code-block:: python

            from audio_recorder import AudioRecorder

            recorder = AudioRecorder(sample_rate=16000, channels=1)

            # Start recording
            recorder.start()
            input("Recording... Press Enter to stop.")  # Wait for user input to stop
            audio_data = recorder.stop()

            # Save the recorded audio to a file
            recorder.save("output.wav")

            # Alternatively, get the audio data as a BytesIO object
            audio_bytes = audio_data
    """

    def __init__(self, sample_rate=16000, channels=1):
        """
        Initializes the AudioRecorder instance.

        Args:
            sample_rate (int): The sample rate for the recording (e.g., 16000 Hz).
            channels (int): The number of audio channels (1 for mono, 2 for stereo).
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.is_recording = False
        self.audio_frames = []

    def _callback(self, indata, frames, time, status):
        """
        Internal callback function to handle incoming audio data from the stream.

        Args:
            indata (numpy.ndarray): The recorded audio data as a NumPy array.
            frames (int): The number of frames in the current audio block.
            time (CData): The time of the audio block (unused).
            status (sounddevice.CallbackFlags): Status flags from the stream.
        """
        if status:
            raise RuntimeError(f"Stream encountered a status: {status}")
        self.audio_frames.append(indata.copy())

    def start(self):
        """
        Starts recording audio from the microphone.

        Raises:
            RuntimeError: If a recording is already in progress.
        """
        if self.is_recording:
            raise RuntimeError("Recording is already in progress.")

        self.audio_frames = []
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self.stream.start()
        self.is_recording = True

    def stop(self):
        """
        Stops the recording and returns the audio data as a bytes-like object.

        Returns:
            io.BytesIO: Bytes-like object containing the WAV audio data.

        Raises:
            RuntimeError: If no recording is in progress.
        """
        if not self.is_recording:
            raise RuntimeError("No recording is in progress to stop.")

        self.stream.stop()
        self.stream.close()
        self.is_recording = False

        # Combine all recorded frames into a single NumPy array
        audio_data = np.concatenate(self.audio_frames, axis=0)

        # Save the recorded audio to a BytesIO object in WAV format using SoundFile
        audio_buffer = io.BytesIO()
        with sf.SoundFile(
            audio_buffer,
            mode="x",
            samplerate=self.sample_rate,
            channels=self.channels,
            format="WAV",
            subtype="PCM_16",
        ) as sf_file:
            sf_file.write(audio_data)

        # Rewind the buffer to the beginning
        audio_buffer.seek(0)
        return audio_buffer

    def save(self, filename):
        """
        Saves the recorded audio to a file in WAV format.

        Args:
            filename (str): The path to the file where the audio will be saved.

        Raises:
            RuntimeError: If a recording is in progress.
        """
        if self.is_recording:
            raise RuntimeError(
                "Cannot save while recording is in progress. Stop the recording first."
            )

        # Combine all recorded frames into a single NumPy array
        audio_data = np.concatenate(self.audio_frames, axis=0)

        # Save the audio data to a file using SoundFile
        sf.write(filename, audio_data, self.sample_rate, format="WAV", subtype="PCM_16")
