# -*- coding: UTF-8 -*-

from openai import OpenAI
import os
import subprocess
import sys
import json
import shutil
import init

client = OpenAI()

def output(output_path, transcript, response_format):
    with open(output_path, "w", encoding="utf-8") as output_file:
        if response_format == "json" or response_format == "verbose_json":
            json.dump(transcript, output_file, indent=4)
        else:
            output_file.write(transcript)

def compare_files(file1_path, file2_path):
    with open(file1_path, "rb") as file1, open(file2_path, "rb") as file2:
        content1 = file1.read()
        content2 = file2.read()

    return content1 == content2

def whisper_translate(file, model, prompt, response_format, temperature):
    if prompt == "":
        return client.audio.translations.create(file=file, model=model, response_format=response_format, \
                                      temperature=temperature)
    else:
        return client.audio.translations.create(file=file, model=model, prompt=prompt, response_format=response_format, \
                                      temperature=temperature)

def whisper_transcribe(file, model, prompt, response_format, temperature, language):
    if prompt == "":
        if language == "auto":
            return client.audio.transcriptions.create(file=file, model=model, response_format=response_format, \
                                          temperature=temperature)
        else:
            return client.audio.transcriptions.create(file=file, model=model, response_format=response_format, \
                                          temperature=temperature, language=language)
    else:
        if language == "auto":
            return client.audio.transcriptions.create(file=file, model=model, prompt=prompt, response_format=response_format, \
                                          temperature=temperature)
        else:
            return client.audio.transcriptions.create(file=file, model=model, prompt=prompt, response_format=response_format, \
                                          temperature=temperature, language=language)

def gpt_punctuation(transcript, gpt_model):
    prompt = "Add the punctuation for the following text.\n" + transcript

    completion = client.chat.completions.create(
        model = gpt_model,
        messages = [
            {"role": "system", "content": "Do not explain. Just follow the instructions."},
            {"role": "function", "name": "add_punctuation_to_text", "content": prompt}
        ]
    )
    return completion

# MAIN LOGIC
def user_interact(supported_file_types, supported_output_formats):

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

    return filenames, work_dir

def process_audios(filenames, work_dir, preprocess_dir, tmp_output_path, output_file_ext, \
                   translation, model, prompt, response_format, temperature, language, gpt_model, punctuation):
    MAX_FILE_SIZE_MB = 25
    preprocess_cnt = 0
    transcribe_cnt = 0

    for filename in filenames:
        isSame = False

        input_file_path = os.path.join(work_dir, filename)
        preprocess_filename = str(preprocess_cnt) + ".wav"
        preprocess_path = os.path.join(preprocess_dir, preprocess_filename)
        print(f"Converting {filename} to WAV...\n")

        subprocess.run(["ffmpeg", "-loglevel", "error", "-i", input_file_path, \
                    "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", tmp_output_path])
        print(f"Converted {filename} to ffmpeg_tmp.wav\n")

        preprocess_files = os.listdir(preprocess_dir)
        for preprocess_file in preprocess_files:
            preprocess_file_path = os.path.join(preprocess_dir, preprocess_file)
            if os.path.getsize(tmp_output_path) == os.path.getsize(preprocess_file_path):
                os.remove(tmp_output_path)
                isSame = True
                print(f"Files {tmp_output_path} and {preprocess_file_path} are same. Skipping...")
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

        if punctuation == "False" or response_format != "text":
            continue

        punctuation_output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + "_punctuation" + output_file_ext)

        print("Adding punctuation to the transcript...\n")

        transcript_punctuation = gpt_punctuation(str(transcript), gpt_model).choices[0].message
        print(transcript_punctuation)

        output(punctuation_output_path, transcript_punctuation, response_format)
        print(f"\nTranscript with punctuation output saved in file {punctuation_output_path}\n")

def cleanup(preprocess_dir):
    init.delete_all_files_in_directory(preprocess_dir)
    print(f"Deleting all files in preprocess directory {preprocess_dir}")
    print(f"\nPROGRAM EXECUTED SUCCESSFULLY!")

def main():
    supported_file_types = [".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", "ogg", ".wav", ".webm"]
    supported_output_formats = ["json", "text", "srt", "verbose_json", "vtt"]
    supported_models = ["whisper-1"]

    if hasattr(sys, 'frozen'):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    config_dir = os.path.join(base_path, "./config")
    config_path = os.path.join(config_dir, "config.ini")
    tmp_output_dir = os.path.join(base_path, "tmp")
    tmp_output_path = os.path.join(tmp_output_dir, "ffmpeg_tmp.wav")
    preprocess_dir = os.path.join(base_path, "preprocess_audio")
    loop_trigger_path = os.path.join(preprocess_dir, "loop_trigger")

    config_values = init.load_config(config_dir, config_path, tmp_output_dir, tmp_output_path, preprocess_dir, loop_trigger_path)

    client.api_key = os.environ.get["OPENAI_API_KEY"] or config_values["openai_api_key"]
    translation = config_values["translation"]
    model = config_values["model"]
    prompt = config_values["prompt"]
    response_format = config_values["response_format"]
    temperature = config_values["temperature"]
    language = config_values["language"]
    gpt_model = config_values["gpt_model"]
    punctuation = config_values["punctuation"]

    output_file_ext, model = init.is_config_values_valid(response_format, supported_output_formats, model, supported_models)

    filenames, work_dir = user_interact(supported_file_types, supported_output_formats)

    process_audios(filenames, work_dir, preprocess_dir, tmp_output_path, output_file_ext, \
                   translation, model, prompt, response_format, temperature, language, gpt_model, punctuation)

    cleanup(preprocess_dir)

    os.system("pause")


if __name__ == "__main__":
    main()
