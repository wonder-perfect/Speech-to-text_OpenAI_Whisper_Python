# -*- coding: UTF-8 -*-

import configparser
import os

# Generate default config file if it's not exsist
def generate_config(config_path):
    if os.path.exists(config_path):
        os.remove(config_path)
    config_ini = '# -*- coding: UTF-8 -*-\n\n[Settings]\nopenai_api_key = your_api_key\ntranslation = False\nmodel = whisper-1\n\
prompt = \nresponse_format = text\ntemperature = 0\nlanguage = auto\n\n[GPT]\nmodel = gpt-3.5-turbo\npunctuation = False\n'
    with open(config_path, "w", encoding='utf-8') as config_file:
        config_file.write(config_ini)

# Delete all the files in the directory
def delete_all_files_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Initialize working environment
def load_config(config_path, tmp_output_dir, tmp_output_path, preprocess_dir, loop_trigger_path):

    # Create tmp files and dirs
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

    # Read the config file
    config = configparser.ConfigParser()

    with open(config_path, encoding='utf-8') as config_file:
        config.read_file(config_file)

    try:
        openai_api_key = config.get("Settings", "openai_api_key")
    except configparser.NoSectionError:
        generate_config(config_path)
        print('\n\033[93mWARN: Section "Settings" not found in config.ini\n\
    Generating default config file...\033[0m')
    except configparser.NoOptionError:
        generate_config(config_path)
        print('\n\033[93mWARN: Option "openai_api_key" not found in config.ini\n\
Generating default config file...\033[0m')

    try:
        translation = config.get("Settings", "translation")
    except configparser.NoOptionError:
        translation = False
        print(f'\n\033[93mWARN: Option "translation" in section "Settings" not found in config.ini\n\
Translation set to {translation}.\033[0m')

    try:
        model = config.get("Settings", "model")
    except configparser.NoOptionError:
        model = "whisper-1"
        print(f'\n\033[93mWARN: Option "model" in section "Settings" not found in config.ini\n\
Model set to {model}.\033[0m')

    try:
        prompt = config.get("Settings", "prompt")
    except configparser.NoOptionError:
        prompt = ""
        print(f'\n\033[93mWARN: Option "prompt" in section "Settings" not found in config.ini\n\
Prompt set to {prompt}.\033[0m')

    try:
        response_format = config.get("Settings", "response_format")
    except configparser.NoOptionError:
        response_format = "text"
        print(f'\n\033[93mWARN: Option "response_format" in section "Settings" not found in config.ini\n\
Response_format set to {response_format}.\033[0m')

    try:
        temperature = config.get("Settings", "temperature")
    except configparser.NoOptionError:
        temperature = 0
        print(f'\n\033[93mWARN: Option "temperature" in section "Settings" not found in config.ini\n\
Temperature set to {temperature}.\033[0m')

    try:
        language = config.get("Settings", "language")
    except configparser.NoOptionError:
        language = "auto"
        print(f'\n\033[93mWARN: Option "language" in section "Settings" not found in config.ini\n\
Language set to {language}.\033[0m')


    try:
        gpt_model = config.get("GPT", "model")
    except configparser.NoOptionError:
        gpt_model = "gpt-3.5-turbo"
        print(f'\n\033[93mWARN: Option "model" in section "GPT" not found in config.ini\n\
GPT_Model set to {gpt_model}.\033[0m')
    
    try:
        punctuation = config.get("GPT", "punctuation")
    except configparser.NoOptionError:
        punctuation = "True"
        print(f'\n\033[93mWARN: Option "punctuation" in section "GPT" not found in config.ini\n\
Puncuation set to {punctuation}.\033[0m')
        
    config_values = {
        "openai_api_key": openai_api_key,
        "translation": translation,
        "model": model,
        "prompt": prompt,
        "response_format": response_format,
        "temperature": temperature,
        "language": language,
        "gpt_model": gpt_model,
        "punctuation": punctuation
    }

    print("\nConfig loaded successfully.")
    
    return config_values

# Check if config values are valid
def is_config_values_valid(response_format, supported_output_formats, model, supported_models):

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

    if model in supported_models:
        model
    else:
        model = supported_models[0]
        print(f"\n\033[93mWARN: Unsupported model. Model set to {model}.\033[0m")
    
    return output_file_ext, model
