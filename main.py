# -*- coding: UTF-8 -*-

import openai
import os
import subprocess

MAX_FILE_SIZE_MB = 25
openai.api_key = "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"
supported_file_types = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]

WARN_cnt = 0

print("\n\033[94mLIMITATION: 25MB\nFILE TYPES SUPPORTED: mp3 mp4 mpeg mpga m4a wav webm\033[0m\n\n\
\033[93mPlease remove the same files in different extensions!\n\
The program will auto convert supported files in the working directory into WAV files!!!\033[0m")

work_dir = input("Enter the directory your audio file located\n\
(Current path will be used as working directory if nothing is entered): ")
if work_dir == "":
    work_dir = os.getcwd()
    print(f"Nothing entered. Changing working directory to current path {work_dir}.\n")
else:
    print(f"Changing working directory to {work_dir}.\n")

audio_filename = input("Enter the audio file name you want to transcribe\n\
(All supported file types will be transcribed if nothing is entered): ")
if audio_filename == "":
    filenames = [filename for filename in os.listdir(work_dir) \
                 if os.path.isfile(os.path.join(work_dir, filename)) and \
                    os.path.splitext(filename)[1].lower() in supported_file_types]
    print("Nothing entered. Transcribing all supported files in working directory.\n\n")
else:
    print(f"Transcribing {audio_filename}\n\n")
    filenames = [audio_filename]

for filename in filenames:
    path = os.path.join(work_dir, filename)

    if os.path.splitext(filename)[1].lower() != ".wav":
        print(f"Converting {filename} to WAV...\n")
        output_wav_filename = os.path.splitext(filename)[0] + ".wav"
        if output_wav_filename in filenames:
            print(f"\033[93mWARN: WAV file {output_wav_filename} already exists, skipping...\n\
WARN: This program only checks if the filename is the same. Please rename the file if the files are different!\033[0m\n")
            WARN_cnt += 1
            continue
        output_wav_path = os.path.join(work_dir, output_wav_filename)
        subprocess.run(["ffmpeg", "-i", path, output_wav_path])
        print(f"Converted {filename} to {output_wav_filename}\n")
        path = output_wav_path

    file_size_mb = os.path.getsize(path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(f"\033[93mWARN: File {filename} is larger than {MAX_FILE_SIZE_MB} and cannot be transcribed!\033[0m\n")
        WARN_cnt += 1
        continue

    audio_file = open(path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(f"Output from {os.path.basename(path)}:")
    print(transcript["text"])
    print()

if WARN_cnt == 0:
    print(f"\n\nPROGRAM EXECUTED SUCCESSFULLY WITH {WARN_cnt} WARNINGS")
else:
    print(f"\033[93m\n\nPROGRAM EXECUTED SUCCESSFULLY WITH {WARN_cnt} WARNINGS\033[0m")
os.system("pause")