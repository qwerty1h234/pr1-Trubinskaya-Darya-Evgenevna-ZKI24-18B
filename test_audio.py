"""Проверки реального декодера SDL без физического аудиоустройства."""

import os
import tempfile
import time
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from pygame import mixer

from app import AudioPlayer
from linked_list import Composition


class AudioTests(unittest.TestCase):
    """Проверить запуск, окончание и остановку звука."""

    def test_playback_and_stop(self) -> None:
        """Декодировать WAV, дождаться окончания, повторить и остановить."""
        mixer.quit()
        with patch.dict(os.environ, {"SDL_AUDIODRIVER": "dummy"}):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "проверка.wav"
                with wave.Wave_write(str(path)) as output:
                    output.setparams((1, 2, 44100, 0, "NONE", "not compressed"))
                    output.writeframes(b"\x00\x00" * 11025)
                player = AudioPlayer()
                try:
                    composition = Composition.from_path(str(path))
                    player.play(composition)
                    self.assertTrue(player.is_playing())
                    deadline = time.monotonic() + 5
                    while player.is_playing() and time.monotonic() < deadline:
                        time.sleep(0.02)
                    self.assertFalse(player.is_playing())
                    player.play(composition)
                    player.stop()
                    self.assertFalse(player.is_playing())
                    with self.assertRaises(FileNotFoundError):
                        player.play(Composition("Нет файла", str(path) + ".missing"))
                finally:
                    player.stop()
                    mixer.quit()
