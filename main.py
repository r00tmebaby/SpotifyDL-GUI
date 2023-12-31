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

import os
import subprocess
import threading

from layout import sg, window


def exec_command(commands: str, output_file, windows: sg.Window, dl: bool = True) -> None:
    """
    Executes a given command in a subprocess and handles output.

    This function executes a specified command using the subprocess module. It captures the command's output and writes it to a specified file. If the 'dl' parameter is True, it specifically handles downloading processes, updating a progress bar in the GUI and managing the download state. For non-downloading processes (when 'dl' is False), it simply writes the command output to the file.

    Parameters:

    :param commands: (str) The command to be executed in the subprocess.
    :param output_file: The file path where the command's output will be written.
    :param windows: (sg.Window): The PySimpleGUI window object used for updating the GUI elements.
    :param dl: (bool, optional) A flag to indicate whether the command is for downloading (True) or a general command (False). Defaults to True.

    Returns:
    - None
    """
    process = subprocess.Popen(
        commands,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        encoding="cp1251",
        universal_newlines=True,
    )
    if dl:
        num_songs_downloaded = 0
        total_songs = None
        window["-download-"].update(disabled=True)
        with open(output_file, "a", encoding="cp1251") as file:
            for line in process.stdout:
                if "Found" in line and "songs" in line:
                    total_songs = int(line.split()[1])
                    window["PROGRESS_BAR"].update_bar(
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
                    process.terminate()
                    break
    else:
        with open(output_file, "a") as file:
            process.stdin.write("y\n")
            process.stdin.flush()

            for line in iter(process.stdout.readline, ""):
                file.write(line)
                file.flush()

    process.wait()


def main_gui() -> None:
    output_file = "command_output.txt"  # Define the output file
    if os.path.isfile(output_file):
        os.remove(output_file)
    last_size = -1
    while True:
        event, values = window.read(1)

        if event == sg.WIN_CLOSED or event == "Exit":
            break
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
            command += (
                f" --output \"{values['OUTPUT-DIRECTORY']}\""
                if values["OUTPUT-DIRECTORY"]
                else ""
            )
            command += f" --threads {values['THREADS']}" if values["THREADS"] else ""
            threading.Thread(
                target=exec_command,
                args=(
                    command,
                    output_file,
                    window,
                    True,
                ),
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
                with open(output_file, "r") as file:
                    window["OUTPUT"].update(file.read())
                last_size = current_size
    window.close()


if __name__ == "__main__":
    threading.Thread(target=main_gui).start()
