# -*- coding: UTF-8 -*-

import openai
import os
import subprocess
import configparser
import sys
import json

WARN_cnt = 0


def whisper_translate(file, model, prompt, response_format, temperature):
    if prompt == "":
        return openai.Audio.translate(file=file, model=model, response_format=response_format, \
                                      temperature=temperature)
    else:
        return openai.Audio.translate(file=file, model=model, prompt=prompt, response_format=response_format, \
                                      temperature=temperature)

def whisper_transcribe(file, model, prompt, response_format, temperature, language):
    if prompt == "":
        if language == "auto":
            return openai.Audio.transcribe(file=file, model=model, response_format=response_format, \
                                          temperature=temperature)
        else:
            return openai.Audio.transcribe(file=file, model=model, response_format=response_format, \
                                          temperature=temperature, language=language)
    else:
        if language == "auto":
            return openai.Audio.transcribe(file=file, model=model, prompt=prompt, response_format=response_format, \
                                          temperature=temperature)
        else:
            return openai.Audio.transcribe(file=file, model=model, prompt=prompt, response_format=response_format, \
                                          temperature=temperature, language=language)


if hasattr(sys, 'frozen'):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_path, 'config.ini')

if os.path.exists(config_path):
    print("\nconfig.ini file found. Loading config...")
else:
    print("\033[91mERR: config.ini file not found!\n\
Please check if the file is located in the same directory with program file!\033[0m")
    os.system("pause")
    sys.exit(1)

config = configparser.ConfigParser()

with open(config_path, encoding='utf-8') as config_file:
    config.read_file(config_file)


try:
    openai.api_key = config.get("Settings", "openai_api_key")
except configparser.NoSectionError:
    print('\n\033[91mERR: Section "Settings" not found in config.ini\033[0m')
    os.system("pause")
    sys.exit(1)
except configparser.NoOptionError:
    print('\n\033[91mERR: Option "openai_api_key" not found in config.ini\033[0m')
    os.system("pause")
    sys.exit(1)

try:
    translation = config.get("Settings", "translation")
except configparser.NoOptionError:
    translation = False
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "translation" not found in config.ini\nTranslation set to {translation}.\033[0m')

try:
    model = config.get("Settings", "model")
except configparser.NoOptionError:
    model = "whisper-1"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "model" not found in config.ini\nModel set to {model}.\033[0m')

try:
    prompt = config.get("Settings", "prompt")
except configparser.NoOptionError:
    prompt = ""
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "prompt" not found in config.ini\nPrompt set to {prompt}.\033[0m')

try:
    response_format = config.get("Settings", "response_format")
except configparser.NoOptionError:
    response_format = "text"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "response_format" not found in config.ini\nResponse_format set to {response_format}.\033[0m')

try:
    temperature = config.get("Settings", "temperature")
except configparser.NoOptionError:
    temperature = 0
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "temperature" not found in config.ini\nTemperature set to {temperature}.\033[0m')

try:
    language = config.get("Settings", "language")
except configparser.NoOptionError:
    language = "auto"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "language" not found in config.ini\nTemperature set to {language}.\033[0m')

print("\nConfig loaded successfully.")


MAX_FILE_SIZE_MB = 25
supported_file_types = [".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", "ogg", ".wav", ".webm"]
supported_output_formats = ["json", "text", "srt", "verbose_json", "vtt"]
output_ext_mapping = {
    "json": ".json",
    "text": ".txt",
    "srt": ".srt",
    "verbose_json": ".verbose_json",
    "vtt": "vtt",
}

if response_format in supported_output_formats:
    output_file_ext = output_ext_mapping[response_format]
else:
    response_format = supported_output_formats[1]
    output_file_ext = output_ext_mapping[response_format]
    print(f"\n\033[93mWARN: Unsupported response_format. Response_format set to {response_format}.\033[0m")

supported_models = ["whisper-1"]

if model in supported_models:
    model
else:
    model = supported_models[0]
    print(f"\n\033[93mWARN: Unsupported model. Model set to {model}.\033[0m")

print(f"\n\033[94mLIMITATION: 25MB\nINPUT FILE TYPES SUPPORTED: {supported_file_types}\n\
OUTPUT FORMAT SUPPORTED: {supported_output_formats}\033[0m\n\n\
\033[93mPlease remove the same files in different extensions!\n\
The program will auto convert supported files in the working directory into WAV files!!!\033[0m")

work_dir = input("Enter the directory your audio file located\n\
(Current path will be used as working directory if nothing is entered): ")
if work_dir == "":
    work_dir = os.getcwd()
    print(f"Nothing entered. Changing working directory to current path {work_dir}\n")
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

    with open(path, "rb") as audio_file:
        if translation == "True":
            transcript = whisper_translate(audio_file, model, prompt, response_format, temperature)
            print(f"Output from {path} (Translation: {translation}, Model: {model}, Prompt: {prompt},\
Response_format: {response_format}, Temperature: {temperature}):")
        else:
            transcript = whisper_transcribe(audio_file, model, prompt, response_format, temperature, language)
            print(f"Output from {path} (Translation: {translation}, Model: {model}, Prompt: {prompt},\
Response_format: {response_format}, Temperature: {temperature}, Language: {language}):")
    
    print(transcript)
    
    output_path = os.path.splitext(path)[0] + output_file_ext
    
    with open(output_path, "w", encoding="utf-8") as output_file:
        if response_format == "json" or response_format == "verbose_json":
            json.dump(transcript, output_file, intend=4)
        else:
            output_file.write(transcript)

print(f"Transcript ouput saved in file {output_path}")

if WARN_cnt == 0:
    print(f"\nPROGRAM EXECUTED SUCCESSFULLY WITH {WARN_cnt} WARNINGS")
else:
    print(f"\033[93m\n\nPROGRAM EXECUTED SUCCESSFULLY WITH {WARN_cnt} WARNINGS\033[0m")
os.system("pause")
