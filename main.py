import os
import subprocess
import threading

from layout import sg, window


def exec_command(commands: str, output_file, window, dl: bool = True):
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
                    window["PROGRESS_BAR"].update_bar(
                        num_songs_downloaded
                    )  # Update the progress bar

                file.write(line)
                file.flush()
                if total_songs and num_songs_downloaded == total_songs:
                    file.write(f"\nDownloaded successfully {total_songs} songs.")
                    window["-download-"].update(disabled=False)
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


def main_gui():
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
