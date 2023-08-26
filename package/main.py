# -*- coding: UTF-8 -*-

import openai
import os
import subprocess
import configparser
import sys
import json
import shutil

WARN_cnt = 0


def generate_config(config_path):
    if os.path.exists(config_path):
        os.remove(config_path)
    config_ini = '# -*- coding: UTF-8 -*-\n\n[Settings]\nopenai_api_key = your_api_key\ntranslation = False\nmodel = whisper-1\n\
prompt = \nresponse_format = text\ntemperature = 0\nlanguage = auto\n\n[GPT]\nmodel=gpt-3.5-turbo\npunctuation=True\n'
    with open(config_path, "w", encoding='utf-8') as config_file:
        config_file.write(config_ini)


def output(output_path, transcript, response_format):
    with open(output_path, "w", encoding="utf-8") as output_file:
        if response_format == "json" or response_format == "verbose_json":
            json.dump(transcript, output_file, indent=4)
        else:
            output_file.write(transcript)


def delete_all_files_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def compare_files(file1_path, file2_path):
    with open(file1_path, "rb") as file1, open(file2_path, "rb") as file2:
        content1 = file1.read()
        content2 = file2.read()

    return content1 == content2


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
tmp_output_dir = os.path.join(base_path, "tmp")
tmp_output_path = os.path.join(tmp_output_dir, "ffmpeg_tmp.wav")
preprocess_dir = os.path.join(base_path, "preprocess_audio")
loop_trigger_path = os.path.join(preprocess_dir, "loop_trigger")

if os.path.exists(preprocess_dir):
    delete_all_files_in_directory(preprocess_dir)
else:
    os.mkdir(preprocess_dir)

with open(loop_trigger_path, "w") as loop_trigger:
    loop_trigger.write("This file is for triggering the loop. Do not move!")

if os.path.exists(tmp_output_path):
    os.remove(tmp_output_path)
    print(f"Exising tmp file {tmp_output_path} found, deleting...")
elif not os.path.exists(tmp_output_dir):
    os.mkdir(tmp_output_dir)
    print(f"Making new tmp directory {tmp_output_dir} ...\n")

if os.path.exists(config_path):
    print("\nconfig.ini file found. Loading config...")
else:
    print("\033[93mWARN: config.ini file not found!\nGenerating config file...")
    generate_config(config_path)

config = configparser.ConfigParser()

with open(config_path, encoding='utf-8') as config_file:
    config.read_file(config_file)


try:
    openai.api_key = config.get("Settings", "openai_api_key")
except configparser.NoSectionError:
    generate_config(config_path)
    WARN_cnt += 1
    print('\n\033[93mWARN: Section "Settings" not found in config.ini\n\
Generating default config file...\033[0m')
except configparser.NoOptionError:
    generate_config(config_path)
    WARN_cnt += 1
    print('\n\033[93mWARN: Option "openai_api_key" not found in config.ini\n\
Generating default config file...\033[0m')

try:
    translation = config.get("Settings", "translation")
except configparser.NoOptionError:
    translation = False
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "translation" in section "Settings" not found in config.ini\n\
Translation set to {translation}.\033[0m')

try:
    model = config.get("Settings", "model")
except configparser.NoOptionError:
    model = "whisper-1"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "model" in section "Settings" not found in config.ini\n\
Model set to {model}.\033[0m')

try:
    prompt = config.get("Settings", "prompt")
except configparser.NoOptionError:
    prompt = ""
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "prompt" in section "Settings" not found in config.ini\n\
Prompt set to {prompt}.\033[0m')

try:
    response_format = config.get("Settings", "response_format")
except configparser.NoOptionError:
    response_format = "text"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "response_format" in section "Settings" not found in config.ini\n\
Response_format set to {response_format}.\033[0m')

try:
    temperature = config.get("Settings", "temperature")
except configparser.NoOptionError:
    temperature = 0
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "temperature" in section "Settings" not found in config.ini\n\
Temperature set to {temperature}.\033[0m')

try:
    language = config.get("Settings", "language")
except configparser.NoOptionError:
    language = "auto"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "language" in section "Settings" not found in config.ini\n\
Language set to {language}.\033[0m')


try:
    gpt_model = config.get("GPT", "model")
except configparser.NoOptionError:
    gpt_model = "gpt-3.5-turbo"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "model" in section "GPT" not found in config.ini\n\
GPT_Model set to {gpt_model}.\033[0m')
    
try:
    punctuation = config.get("GPT", "punctuation")
except configparser.NoOptionError:
    punctuation = "True"
    WARN_cnt += 1
    print(f'\n\033[93mWARN: Option "punctuation" in section "GPT" not found in config.ini\n\
Puncuation set to {punctuation}.\033[0m')

print("\nConfig loaded successfully.")


def gpt_punctuation(transcript):
    prompt = "Add the punctuation for the following text.\n" + transcript

    completion = openai.ChatCompletion.create(
        model = gpt_model,
        messages = [
            {"role": "system", "content": "Do not explain. Just follow the instructions."},
            {"role": "function", "name": "add_punctuation_to_text", "content": prompt}
        ]
    )
    return completion


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
OUTPUT FORMAT SUPPORTED: {supported_output_formats}\033[0m\n")

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

preprocess_cnt = 0
transcribe_cnt = 0

for filename in filenames:
    isSame = False

    input_file_path = os.path.join(work_dir, filename)
    preprocess_filename = str(preprocess_cnt) + ".wav"
    preprocess_path = os.path.join(preprocess_dir, preprocess_filename)
    print(f"Converting {filename} to WAV...\n")

    subprocess.run(["ffmpeg", "-loglevel", "error", "-i", input_file_path, "-ac", "1", "-ar", "16000", tmp_output_path])
    print(f"Converted {filename} to ffmpeg_tmp.wav\n")

    preprocess_files = os.listdir(preprocess_dir)
    for preprocess_file in preprocess_files:
        preprocess_file_path = os.path.join(preprocess_dir, preprocess_file)
        if os.path.getsize(tmp_output_path) == os.path.getsize(preprocess_file_path):
            os.remove(tmp_output_path)
            isSame = True
            break
    
    if isSame:
        isSame = False
        continue

    shutil.move(tmp_output_path, preprocess_path)
    preprocess_cnt += 1

    if transcribe_cnt >= preprocess_cnt:
        continue

    file_size_mb = os.path.getsize(preprocess_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(f"\033[93mWARN: File {filename} is larger than {MAX_FILE_SIZE_MB} and cannot be transcribed!\033[0m\n")
        WARN_cnt += 1
        transcribe_cnt += 1
        continue
    
    output_dir = os.path.join(work_dir, "output")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    transcript_output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + "_transcript" + output_file_ext)

    with open(preprocess_path, "rb") as audio_file:
        if translation == "True":
            transcript = whisper_translate(audio_file, model, prompt, response_format, temperature)
            print(f"Output from {input_file_path} (Translation: {translation}, Model: {model}, Prompt: {prompt},\
Response_format: {response_format}, Temperature: {temperature}):\n")
        else:
            transcript = whisper_transcribe(audio_file, model, prompt, response_format, temperature, language)
            print(f"Output from {input_file_path} (Translation: {translation}, Model: {model}, Prompt: {prompt},\
Response_format: {response_format}, Temperature: {temperature}, Language: {language}):\n")
    
    print(transcript)
    transcribe_cnt += 1

    output(transcript_output_path, transcript, response_format)
    print(f"Transcript output saved in file {transcript_output_path}\n")

    if punctuation == "False":
        continue

    punctuation_output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + "_punctuation" + output_file_ext)

    print("Adding punctuation to the transcript...\n")

    transcript_punctuation = gpt_punctuation(str(transcript))["choices"][0]["message"]["content"]
    print(transcript_punctuation)

    output(punctuation_output_path, transcript_punctuation, response_format)
    print(f"Transcript with punctuation output saved in file {punctuation_output_path}\n")


if WARN_cnt == 0:
    print(f"\nPROGRAM EXECUTED SUCCESSFULLY WITH {WARN_cnt} WARNINGS")
else:
    print(f"\033[93m\n\nPROGRAM EXECUTED SUCCESSFULLY WITH {WARN_cnt} WARNINGS\033[0m")
    
os.system("pause")
