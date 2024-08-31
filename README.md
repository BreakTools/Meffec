# Meffec

**Infrastructure for real-time scriptable app triggered show effects.**
![Meffec banner](https://github.com/user-attachments/assets/5a5bd1db-a20f-49eb-ab6d-3649a0162a0a)

## What does it do?

Simply put, Meffec is a system specifically designed for realtime show effects that allows you to easily trigger Python scripts through a mobile app. Originally designed for hosting D&D games, it has now grown to be a flexible system for all types of realtime effects. The system consists of a desktop application, a websocket server backend and a mobile app. It makes it easy to establish an atmosphere using audio and lighting with a click of a single button, so you can set the mood without worrying about the tech.

## Why was it made?

I really, really enjoy creating immersive experiences. Be it for D&D or whenever I throw a big halloween party. I also really like having one button for things.
Just imagine this: _A bossfight is starting. The party has been working up to this point for months. You've been monologuing for minutes and the big fight is about to break out._ The atmoshphere needs to be just right to suit the moment. Do you now want to first use your DMX software to turn the lights to red, then open Spotify to change your tavern music to some fighting music, perhaps open YouTube for some dungeon ambiance and then physically press the button on your smoke machine to create some ambiance? I don't. Existing solutions for this like QLab seemed way too advanced and don't provide the simple flexibily of being able to run any ol' Python script, so I decided to make my own system.

## How does it work?

Let's go over implementing the above scenario. The Meffec Controller desktop application scans a given folder for scripts that match the Meffec python format, which is simply any python file which has a `get_effects_info()` function:

```python
def get_effect_info() -> dict:
    return {
        "category": "D&D Presets",
        "name": "Fighting",
        "description": "Plays intense fighting music, triggers smoke machine and turns lights red.",
    }
```

The controller will send this information to the server, which will then be sent to the app. In the app this script now shows up as:
[image here]

Effects scripts should implement a `run_effect` function, which will be triggered when you press the button in the app:

```python
def run_effect(meffec_classes) -> None:
    meffec_classes.audio_handler.play_new_music(
        Path(__file__).parent / "audio_files" / "music" / "fighting.mp3"
    )
    meffec_classes.audio_handler.play_ambiance(
        Path(__file__).parent / "audio_files" / "ambiance" / "dungeon.mp3",
        "nature",
    )

    meffec_classes.osc_handler.send_message_to_server(
        "/live/Control_Panel/cue/All_red/activate", 1
    )

    meffec_classes.device_handler.send_device_action(
        "Smoke machine", {"enabled": True}
    )
    meffec_classes.timing_handler.run_function_after_sleep(
        lambda: disable_smoke_machine(meffec_classes), 4
    )


def disable_smoke_machine(meffec_classes) -> None:
    meffec_classes.device_handler.send_device_action(
        "Smoke machine", {"enabled": False}
    )
```

`meffec_classes` are passed to the run_effect function, which are multiple classes for making developing show effects as easy as possible. There's support for as many streams of audio as you want, OSC messaging for interfacing with for example DMX software and you can also send data to custom devices across the Meffec network (I've for example modified my dirt cheap smoke machine so it can be triggered with a NodeMCU that's connected to the Meffec server).

## Setting up your Meffec system

Still working on the documentation, so stay tuned!
