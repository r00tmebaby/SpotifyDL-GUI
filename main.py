"""
SpotifyDL-GUI: A Python-based Graphical User Interface for Downloading Spotify Playlists

This program, SpotifyDL-GUI, leverages the power of Python and PySimpleGUI to provide an intuitive and user-friendly interface for downloading Spotify playlists. It's designed to simplify the process of downloading songs from Spotify, offering a range of customizable options such as selecting the audio source, lyrics source, format, bitrate, and more. The application also integrates with external tools like FFmpeg to handle media file conversions.

Key Features:
- Download Spotify playlists through a simple and interactive GUI.
- Choose from multiple audio and lyrics sources including YouTube, SoundCloud, and others.
- Customize download settings like format, bitrate, and output directory.
- Progress tracking with a real-time updating progress bar.
- Advanced settings for filtering results, headless operation, and cache management.
- Logging tab for monitoring download processes and actions.

The program's main GUI loop handles user interactions, capturing input data and triggering appropriate actions based on user choices. It uses threading to ensure the UI remains responsive during downloads. The `exec_command` function is a core component that executes external commands and manages output for both downloading and non-downloading processes.

Usage:
Run the script and interact with the GUI to choose playlists and download settings. The program will handle the rest, providing updates and logs directly within the GUI.

Dependencies:
- PySimpleGUI for the graphical interface.
- spotdl and FFmpeg for handling Spotify playlist downloading and media file processing.

This script represents a convenient solution for music enthusiasts looking to download and manage their Spotify playlists with ease.

Author: Zdravko Georgiev
Version: 0.0.1
Date: 12.02.2023
"""

import ensurepip
import os
import subprocess
import sys
import threading
from pathlib import Path

from layout import sg, window

current_process = None


def ensure_pip():
    """Ensure pip is installed. If not, install it using ensurepip."""
    try:
        # Check if pip is available
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    # sg.popup_notify("pip is already installed.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        sg.popup_notify("pip is not installed. Installing pip...")
        try:
            ensurepip.bootstrap()
            sg.popup_notify("pip installed successfully.")
        except Exception as e:
            sg.popup_error(f"Failed to install pip: {e}")
            sys.exit(1)  # Exit the program if pip installation fails


def check_and_install_spotdl():
    """Check if spotdl is installed. If not, install it using pip."""
    ensure_pip()  # Ensure pip is available
    try:
        # Check if spotdl is available
        subprocess.run(
            ["spotdl", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # sg.popup_notify("spotdl is already installed.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        sg.popup_notify("spotdl is not installed. Installing now...")
        try:
            # Install spotdl using pip
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "spotdl"], check=True
            )
            sg.popup_notify("spotdl installed successfully.")
        except subprocess.CalledProcessError as e:
            sg.popup_error(f"Failed to install spotdl: {e}")
            sys.exit(1)  # Exit the program if installation fails


def exec_command(
    commands: str,
    output_file,
    windows: sg.Window,
    dl: bool = True,
) -> None:
    """
    Executes a given command in a subprocess and handles output.

    This function executes a specified command using the subprocess module.
    It captures the command's output and writes it to a specified file.
    If the 'dl' parameter is True, it specifically handles downloading processes,
    updating a progress bar in the GUI and managing the download state.
    For non-downloading processes (when 'dl' is False), it simply writes the command output to the file.

    Parameters:

    :param commands: (str) The command to be executed in the subprocess.
    :param output_file: The file path where the command's output will be written.
    :param windows: (sg.Window): The PySimpleGUI window object used for updating the GUI elements.
    :param dl: (bool, optional) A flag to indicate whether the command
        is for downloading (True) or a general command (False). Defaults to True.

    Returns:
    - None
    """
    global current_process
    try:
        current_process = subprocess.Popen(
            commands,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            universal_newlines=True,
        )
        if dl:
            num_songs_downloaded = 0
            total_songs = None
            windows["-download-"].update(disabled=True)
            windows["-stop-"].update(disabled=False)
            with open(output_file, "a", encoding="utf-8") as file:
                for line in current_process.stdout:
                    if "Found" in line and "songs" in line:
                        total_songs = int(line.split()[1]) - 1
                        windows["PROGRESS_BAR"].update_bar(
                            0, total_songs
                        )  # Initialize the progress bar
                    # Prepend number to 'Downloaded' lines
                    if "Downloaded" in line or "Skipping" in line:
                        num_songs_downloaded += 1
                        line = f"{num_songs_downloaded}. {line}"
                        windows["PROGRESS_BAR"].update_bar(
                            num_songs_downloaded
                        )  # Update the progress bar

                    file.write(line)
                    file.flush()
                    if total_songs and num_songs_downloaded == total_songs:
                        file.write(f"\nDownloaded successfully {total_songs} songs.")
                        windows["-download-"].update(disabled=False)
                        current_process.terminate()
                        break
        else:
            with open(output_file, "a") as file:
                current_process.stdin.write("y\n")
                current_process.stdin.flush()

                for line in iter(current_process.stdout.readline, ""):
                    file.write(line)
                    file.flush()

        current_process.wait()
    except threading.ThreadError as e:
        windows["OUTPUT"].print(f"Error: {e}\n")
        windows["-stop-"].update(disabled=True)
    finally:
        current_process = None
        windows["-stop-"].update(disabled=True)


def main_gui() -> None:
    output_file = "command_output.txt"  # Define the output file
    if os.path.isfile(output_file):
        os.remove(output_file)
    last_size = -1
    while True:
        event, values = window.read(1)

        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "-stop-":
            if current_process is not None:
                current_process.terminate()
                current_process.wait()
                window["-download-"].update(disabled=False)
                window["-stop-"].update(disabled=True)
                sg.popup("Download stopped.")
            else:
                sg.popup_error("No active process to stop.")
        elif event == "-download-":
            if not values["URL"]:
                sg.popup_error("Add a valid spotify link")
                continue
            command = f"spotdl {values['URL']}"
            command += (
                f" --audio {values['AUDIO_SOURCE']}" if values["AUDIO_SOURCE"] else ""
            )
            command += (
                f" --lyrics {values['LYRICS_SOURCE']}"
                if values["LYRICS_SOURCE"]
                else ""
            )
            command += f" --format {values['FORMAT']}" if values["FORMAT"] else ""
            command += f" --bitrate {values['BITRATE']}" if values["BITRATE"] else ""
            command += (
                f" --ffmpeg-args \"{values['FFMPEG_ARGS']}\""
                if values["FFMPEG_ARGS"]
                else ""
            )

            Path(values["OUTPUT-DIRECTORY"]).mkdir(parents=True, exist_ok=True)

            command += (
                f" --output \"{values['OUTPUT-DIRECTORY']}\""
                if values["OUTPUT-DIRECTORY"]
                else ""
            )

            # command += f" --threads {values['THREADS']}" if values["THREADS"] else ""
            task = threading.Thread(
                target=exec_command,
                args=(command, output_file, window, True),
                daemon=True,
            ).start()

        elif event == "Install/Check FFmpeg":
            threading.Thread(
                target=exec_command,
                args=(
                    "spotdl --download-ffmpeg",
                    output_file,
                    window,
                    False,
                ),
                daemon=True,
            ).start()

        if os.path.exists(output_file):
            current_size = os.path.getsize(output_file)
            if current_size != last_size:
                with open(output_file, "r", encoding="utf-8") as file:
                    window["OUTPUT"].update(file.read())
                last_size = current_size
    window.close()


if __name__ == "__main__":
    # Check if spotdl is installed
    check_and_install_spotdl()

    # Run the GUI in the main thread
    main_gui()
