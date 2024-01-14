# -*- coding: UTF-8 -*-

import json
import os

DEFAULT_CONFIG = {
    "general": {
        "openai_api_key": "",
        "temperature": "0"
    },
    "audio": {
        "translation": "False",
        "model": "whisper-1",
        "prompt": "",
        "response_format": "text",
        "language": "auto"
    },
    "punctuation": {
        "model": "gpt-3.5-turbo",
        "punctuation": "False"
    }
}

# Generate default config file if it's not exsist
def generate_config(config_dir, config_path):
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    delete_all_files_in_directory(config_dir)
    openai_api_key = input("Enter your OpenAI API Key: ")
    config = DEFAULT_CONFIG
    config["general"]["openai_api_key"] = openai_api_key
    with open(config_path, "w", encoding='utf-8') as config_file:
        json.dump(config, config_file, indent=4)

# Delete all the files in the directory
def delete_all_files_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Initialize working environment
def load_config(config_dir, config_path, tmp_output_dir, tmp_output_path, preprocess_dir, loop_trigger_path, supported_output_formats, supported_models):

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
        config = json.load(open(config_path, encoding='utf-8'))
        print("\nconfig.json file found. Loading config...")
    else:
        generate_config(config_dir, config_path)
        print("\033[93m[WARN]: config.json file not found!\nGenerating config file...\033[0m\n")

    config['audio']['response_format'], config['audio']['model'] = is_config_values_valid(
        config['audio']['response_format'], 
        supported_output_formats, 
        config['audio']['model'], 
        supported_models
    )

    print("\nConfig loaded successfully.")
    
    return config

# Check if config values are valid
def is_config_values_valid(response_format, supported_output_formats, model, supported_models):

    if response_format not in supported_output_formats:
        response_format = supported_output_formats[1]
        print(f"\n\033[93m[WARN]: Unsupported response_format. Response_format set to {response_format}.\033[0m")

    if model not in supported_models:
        model = supported_models[0]
        print(f"\n\033[93m[WARN]: Unsupported model. Model set to {model}.\033[0m")
    
    return response_format, model
