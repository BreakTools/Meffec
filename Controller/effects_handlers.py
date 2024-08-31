"""Effects handling classes that will be available to the Meffec scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import data_structures
from PySide6 import QtCore, QtMultimedia
from pythonosc.udp_client import SimpleUDPClient


class AudioHandler(QtCore.QObject):
    """Class that handles all audio systems, from one-shot audio to looping ambiance sounds."""

    def __init__(self) -> None:
        """Initializes the audio handler."""
        super().__init__()
        self.music = FadeableAudioPlayer()
        self.ambiances = {}
        self.currently_playing = []

    def play_audio(self, audio_file: Path, volume: int = 70) -> None:
        """Single-shot plays the given audio file. Uses QSoundEffect for low latency so
        only supports uncompressed .wavs.

        Args:
            audio_file: The audio file to one-shot play.
            volume: Volume percentage to play audio at.
        """
        sound_effect = QtMultimedia.QSoundEffect()
        sound_effect.setSource(QtCore.QUrl.fromLocalFile(audio_file))
        sound_effect.setVolume(volume / 100)
        sound_effect.play()
        sound_effect.playingChanged.connect(
            lambda: self.garbage_collect_audio(sound_effect)
        )
        self.currently_playing.append(sound_effect)

    def garbage_collect_audio(
        self, sound_effect: QtMultimedia.QSoundEffect
    ) -> None:
        """Removes the given audio from our currently playing list if it's no longer playing.

        Args:
            sound_effect: The QSoundEffect instance that finished playing.
        """
        if not sound_effect.isPlaying():
            self.currently_playing.remove(sound_effect)

    def play_new_music(self, new_music_file: Path, volume=70) -> None:
        """Starts playing the given music.

        Args:
            new_music_file: The music file to play.
        """
        self.music.play_audio(new_music_file, volume=volume)

    def unpause_music(self) -> None:
        """Unpauses the music that was previously paused, if there was any."""
        if not self.music.is_playing():
            self.music.play()

    def pause_music(self, fade=False) -> None:
        """Pauses the currently playing music.

        Args:
            fade: If we should fade out the music.
        """
        if self.music.is_playing():
            self.music.pause(fade)

    def play_ambiance(
        self, ambiance_file: Path, ambiance_category: str, volume=70
    ) -> None:
        """Plays the given ambiance file. If there's ambiance already playing in the given category,
        it will be overwritten by the new ambiance.

        Args:
            ambiance_file: The ambiance file to play.
            ambiance_category: The category of the ambiance (e.g., 'weather', 'people').
        """
        if ambiance_category in self.ambiances:
            self.ambiances[ambiance_category].audio_player.play_audio(
                ambiance_file
            )
            return

        ambiance = data_structures.Ambiance(
            ambiance_category, FadeableAudioPlayer()
        )
        ambiance.audio_player.play_audio(ambiance_file, volume=volume)
        self.ambiances[ambiance_category] = ambiance

    def pause_ambiance(self, ambiance_category: str) -> None:
        """Pauses the currently playing ambiance for the given category.

        Args:
            ambiance_category: The category of the ambiance to pause.
        """
        if ambiance_category in self.ambiances:
            ambiance = self.ambiances[ambiance_category]
            if ambiance.audio_player.is_playing():
                ambiance.pause()

    def pause_all_ambiance(self, fade=False) -> None:
        """Stops the playing of all ambiances.

        Args:
            fade: If the audio should fade out.
        """
        for ambiance in self.ambiances.values():
            if ambiance.audio_player.is_playing():
                ambiance.audio_player.pause(fade)

    def unpause_all_ambiance(self) -> None:
        """Resumes playing of all ambiances."""
        for ambiance in self.ambiances.values():
            if not ambiance.audio_player.is_playing():
                ambiance.audio_player.play()

    def fade_out_all_ambiance_except(
        self, excepted_categories: list[str]
    ) -> None:
        """Fade out playing ambiances except the ones specified."""
        for ambiance in self.ambiances.values():
            if ambiance.category not in excepted_categories:
                ambiance.audio_player.fade_out()


class FadeableAudioPlayer(QtCore.QObject):
    """Audio player that allows for fading when a new audio is played."""

    def __init__(self) -> None:
        """Initializes the audio player by creating our two audio streams."""
        super().__init__()
        self.first_audio_output = QtMultimedia.QAudioOutput()
        self.first_media_player = QtMultimedia.QMediaPlayer()
        self.first_media_player.setAudioOutput(self.first_audio_output)

        self.second_audio_output = QtMultimedia.QAudioOutput()
        self.second_media_player = QtMultimedia.QMediaPlayer()
        self.second_media_player.setAudioOutput(self.second_audio_output)

        self.currently_playing = None

    def play_audio(
        self, audio_path: Path, volume: int = 70, looping=True, fade=True
    ) -> None:
        """Plays the given audio path by calling the right playing function.

        Args:
            audio_path: Path to the audio file.
            volume: Volume percentage to play audio at.
            looping: If the audio should loop.
            fade: If the audio should fade.
        """
        volume = volume / 100

        if self.currently_playing is None:
            self.play_initial_audio(audio_path, volume, looping)
            return

        if not fade:
            self.play_without_fade(audio_path, volume, looping)
            return

        self.fade_to_new_audio(audio_path, volume, looping)

    def play_initial_audio(
        self, audio_path: Path, volume: float, looping: bool
    ) -> None:
        """Fades in audio for the first time.

        Args:
            audio_path: Path to the audio file.
            volume: Volume percentage to play audio at.
            looping: If the audio should loop.
        """
        self.first_media_player.setSource(
            QtCore.QUrl.fromLocalFile(audio_path)
        )
        self.first_media_player.setLoops(
            QtMultimedia.QMediaPlayer.Loops.Infinite if looping else 0
        )
        self.first_media_player.play()
        self.currently_playing = self.first_media_player

        self.fade_in_animation = QtCore.QPropertyAnimation(
            self.first_audio_output, b"volume"
        )
        self.fade_in_animation.setDuration(2000)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(volume)
        self.fade_in_animation.start()

    def play_without_fade(
        self, audio_path: Path, volume: float, looping: bool
    ) -> None:
        """Plays the given audio path without a fading in animation. Useful for audio
        that needs a punchy start.

        Args:
            audio_path: Path to the audio file.
            volume: Volume percentage to play audio at.
            looping: If the audio should loop.
        """
        self.currently_playing.setSource(QtCore.QUrl.fromLocalFile(audio_path))
        self.currently_playing.setLoops(
            QtMultimedia.QMediaPlayer.Loops.Infinite if looping else 0
        )
        self.currently_playing.audioOutput().setVolume(volume)
        self.currently_playing.play()

    def fade_to_new_audio(
        self, audio_path: Path, volume: float, looping: bool
    ):
        """Softly fades in the audio on the track that's currently not playing and slowly fades
        out the currently playing audio using QPropertyAnimations.

        Args:
            audio_path: Path to the audio file.
            volume: Volume percentage to play audio at.
            looping: If the audio should loop.
        """
        fade_out_player = self.currently_playing
        fade_in_player = (
            self.first_media_player
            if self.currently_playing == self.second_media_player
            else self.second_media_player
        )

        fade_in_player.setSource(QtCore.QUrl.fromLocalFile(audio_path))
        fade_in_player.setLoops(
            QtMultimedia.QMediaPlayer.Loops.Infinite if looping else 0
        )

        self.fade_out_animation = QtCore.QPropertyAnimation(
            fade_out_player.audioOutput(), b"volume"
        )
        self.fade_out_animation.setDuration(2000)
        self.fade_out_animation.setStartValue(
            fade_out_player.audioOutput().volume()
        )
        self.fade_out_animation.setEndValue(0)

        self.fade_in_animation = QtCore.QPropertyAnimation(
            fade_in_player.audioOutput(), b"volume"
        )
        self.fade_in_animation.setDuration(2000)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(volume)

        self.fade_out_animation.start()
        self.fade_in_animation.start()
        fade_in_player.play()

        self.fade_out_animation.finished.connect(fade_out_player.stop)

        self.currently_playing = fade_in_player

    def is_playing(self) -> bool:
        """Checks if the currently stored mediaplyer is actively playing.

        Returns:
            If we're currently playing audio.
        """
        return self.currently_playing.isPlaying()

    def pause(self, fade: bool) -> None:
        """Pauses the currently playing audio.

        Args:
            fade: If the audio should fade out.
        """
        if not fade:
            self.currently_playing.pause()
            return

        self.fade_out()

    def play(self) -> None:
        """Plays/unpauses the currently playing audio."""
        self.fade_in_animation = QtCore.QPropertyAnimation(
            self.currently_playing.audioOutput(), b"volume"
        )
        self.fade_in_animation.setDuration(1000)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(
            self.currently_playing.audioOutput().volume()
        )
        self.fade_in_animation.start()
        self.currently_playing.play()

    def fade_out(self) -> None:
        """Fades out the currently playing audio."""
        self.fade_out_animation = QtCore.QPropertyAnimation(
            self.currently_playing.audioOutput(), b"volume"
        )
        self.fade_out_animation.setDuration(2000)
        self.fade_out_animation.setStartValue(
            self.currently_playing.audioOutput().volume()
        )
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.start()
        self.fade_out_animation.finished.connect(self.currently_playing.stop)


class OSCHandler(QtCore.QObject):
    """Class that handles connection to OSC server and sending messages."""

    def __init__(self):
        """Initializes the OSC handler."""
        super().__init__()
        self.connect_to_server()

    def connect_to_server(self):
        """Connects to OSC server using the stored settings."""
        settings = QtCore.QSettings()
        server_url = settings.value(
            data_structures.SettingsKey.OSC_SERVER_URL.value
        )
        server = server_url.split(":")[0]
        port = server_url.split(":")[1]
        self.osc_connection = SimpleUDPClient(server, int(port))

    def send_message_to_server(self, address: str, value: Any) -> None:
        """Sends the given value to the given address on the server.

        Args:
            address: The address to send the value to.
            value: The value to send to the address.
        """
        self.osc_connection.send_message(address, value)


class DeviceHandler(QtCore.QObject):
    """Class that provides utility functions for sending device actions across
    the Meffec network."""

    device_action_sent = QtCore.Signal(Any)

    def send_device_action(self, device_name: str, data: dict) -> None:
        """Sends the device action to the server.

        Args:
            device_name: The name of the device to send the data to.
            data: The data to send.
        """
        self.device_action_sent.emit(
            data_structures.DeviceAction(device_name, data)
        )


class TimingHandler(QtCore.QObject):
    """Class that provides utility functions for handling timing in effects scripts."""

    def run_function_after_sleep(
        self, function: Callable, sleep_in_seconds: int
    ) -> None:
        """Runs the given function after a given delay.

        Args:
            function: The function to run.
            sleep_in_seconds: The delay to use.
        """
        QtCore.QTimer.singleShot(sleep_in_seconds * 1000, function)
