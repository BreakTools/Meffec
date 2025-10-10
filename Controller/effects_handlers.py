"""Effects handling classes that will be available to the Meffec scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PySide6 import QtCore, QtMultimedia
from pythonosc.udp_client import SimpleUDPClient

import data_structures
from models import LogModel


class AudioHandler(QtCore.QObject):
    """Class that handles all audio systems, from one-shot audio to looping ambiance sounds."""

    def __init__(self, log_model: LogModel) -> None:
        """Initializes the audio handler."""
        super().__init__()
        self.log_model = log_model
        self.music = FadeableAudioPlayer()
        self.ambiances = {}
        self.currently_playing = []

        self.media_devices = QtMultimedia.QMediaDevices()
        self.media_devices.audioOutputsChanged.connect(
            self._on_audio_outputs_changed
        )

    def play_audio(
        self, audio_file: Path, volume: int = 70, audio_device_name: str = ""
    ) -> None:
        """Single-shot plays the given audio file.

        Args:
            audio_file: The audio file to one-shot play.
            volume: Volume percentage to play audio at.
            audio_device_name: Optional audio output device to use instead of default.
        """
        sound_effect = data_structures.SoundEffect(
            QtMultimedia.QMediaPlayer(), QtMultimedia.QAudioOutput()
        )

        if audio_device_name:
            sound_effect.audio_output.setDevice(
                self._find_audio_device_from_name(audio_device_name)
            )
            self.log_model.log(
                f"Playing sound effect on custom audio device: {sound_effect.audio_output.device().description()}"
            )

        sound_effect.audio_output.setVolume(volume / 100)
        sound_effect.audio_player.setAudioOutput(sound_effect.audio_output)
        sound_effect.audio_player.setSource(
            QtCore.QUrl.fromLocalFile(str(audio_file))
        )

        def _garbage_collect_self(
            status: QtMultimedia.QMediaPlayer.MediaStatus,
        ) -> None:
            if status == QtMultimedia.QMediaPlayer.MediaStatus.EndOfMedia:
                self.currently_playing.remove(sound_effect)
                sound_effect.audio_output.deleteLater()
                sound_effect.audio_player.deleteLater()

        sound_effect.audio_player.mediaStatusChanged.connect(
            _garbage_collect_self
        )
        self.currently_playing.append(sound_effect)
        sound_effect.audio_player.play()

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

    def _find_audio_device_from_name(
        self, audio_device_name: str
    ) -> QtMultimedia.QAudioDevice:
        """Returns the correct audio device from the given name. Returns the default
        audio output device if no match is found.

        Args:
            audio_device_name: The name of the device to search for.

        Returns:
            The correct audio device, or the default one if no match is found.
        """
        all_audio_output_devices = QtMultimedia.QMediaDevices.audioOutputs()

        for audio_device in all_audio_output_devices:
            if audio_device_name.lower() in audio_device.description().lower():
                return audio_device

        self.log_model.log(
            f"Specified audio output device '{audio_device_name}' could not be found. Using default."
        )
        return QtMultimedia.QMediaDevices.defaultAudioOutput()

    def _on_audio_outputs_changed(self) -> None:
        """Ensures the music and ambiances keep playing on the default audio output
        device if there's an update to the system's audio devices."""
        self.log_model.log("Processing audio device changes...")

        self.music.change_audio_device(
            QtMultimedia.QMediaDevices.defaultAudioOutput()
        )

        for ambiance in self.ambiances:
            self.ambiances[ambiance].audio_player.change_audio_device(
                QtMultimedia.QMediaDevices.defaultAudioOutput()
            )


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

    def change_audio_device(
        self, audio_output_device: QtMultimedia.QAudioDevice
    ) -> None:
        """Changes the audio device on the two audio streams to the new one.

        Args:
            audio_output_device: The new audio device to use
        """
        self.first_audio_output.setDevice(audio_output_device)
        self.second_audio_output.setDevice(audio_output_device)


class OSCHandler(QtCore.QObject):
    """Class that handles connection to OSC server and sending messages."""

    def __init__(self):
        """Initializes the OSC handler."""
        super().__init__()
        self.connect_to_server()
        self.osc_connection = None

    def connect_to_server(self):
        """Connects to OSC server using the stored settings."""
        settings = QtCore.QSettings()
        server_url = settings.value(
            data_structures.SettingsKey.OSC_SERVER_URL.value, "0.0.0.0:2002"
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
        if not self.osc_connection:
            return

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
