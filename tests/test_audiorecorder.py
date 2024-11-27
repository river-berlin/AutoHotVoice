import pytest
from unittest.mock import MagicMock, patch
import numpy as np

# test_my_submodule.py
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from src.autohotvoice.audiorecorder import AudioRecorder


# Mock Data for Testing
@pytest.fixture
def mock_audio_data():
    """Fixture to provide mock audio data."""
    return np.random.rand(16000, 1).astype("float32")  # 1 second of mono audio


# Test Initialization
def test_audio_recorder_initialization():
    recorder = AudioRecorder(sample_rate=16000, channels=1)
    assert recorder.sample_rate == 16000
    assert recorder.channels == 1
    assert not recorder.is_recording
    assert recorder.audio_frames == []


# Test Starting Recording
@patch("sounddevice.InputStream")
def test_start_recording(mock_input_stream):
    recorder = AudioRecorder(sample_rate=16000, channels=1)

    recorder.start()

    mock_input_stream.assert_called_once_with(
        samplerate=16000,
        channels=1,
        dtype="float32",
        callback=recorder._callback,
    )
    mock_input_stream.return_value.start.assert_called_once()
    assert recorder.is_recording
    assert recorder.audio_frames == []


# Test Stop Recording
@patch("sounddevice.InputStream")
@patch("soundfile.SoundFile")
def test_stop_recording(mock_soundfile, mock_input_stream, mock_audio_data):
    recorder = AudioRecorder(sample_rate=16000, channels=1)
    recorder.start()

    # Simulate the audio callback filling frames
    recorder._callback(mock_audio_data, frames=16000, time=None, status=None)
    recorder.stop()

    mock_input_stream.return_value.stop.assert_called_once()
    mock_input_stream.return_value.close.assert_called_once()
    assert not recorder.is_recording

    # Check SoundFile writes the combined audio data
    mock_soundfile.return_value.write.assert_called_once_with(np.concatenate([mock_audio_data], axis=0))


# Test Saving Audio
@patch("soundfile.write")
def test_save_audio(mock_write, mock_audio_data):
    recorder = AudioRecorder(sample_rate=16000, channels=1)

    # Add some audio data
    recorder.audio_frames.append(mock_audio_data)
    recorder.save("test_output.wav")

    mock_write.assert_called_once_with(
        "test_output.wav",
        np.concatenate([mock_audio_data], axis=0),
        16000,
        format="WAV",
        subtype="PCM_16",
    )


# Test Start Recording Error
def test_start_recording_error():
    recorder = AudioRecorder(sample_rate=16000, channels=1)
    recorder.is_recording = True  # Simulate recording in progress

    with pytest.raises(RuntimeError, match="Recording is already in progress."):
        recorder.start()


# Test Stop Recording Error
def test_stop_recording_error():
    recorder = AudioRecorder(sample_rate=16000, channels=1)

    with pytest.raises(RuntimeError, match="No recording is in progress to stop."):
        recorder.stop()


# Test Save While Recording
def test_save_while_recording_error():
    recorder = AudioRecorder(sample_rate=16000, channels=1)
    recorder.is_recording = True  # Simulate recording in progress

    with pytest.raises(RuntimeError, match="Cannot save while recording is in progress. Stop the recording first."):
        recorder.save("test_output.wav")