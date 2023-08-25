# Speech-to-text using OpenAI Whisper in Python

This repository contains Python code that utilizes OpenAI's Whisper ASR (Automatic Speech Recognition) system to convert spoken language into written text.

<!-- If you have an example image, replace "path/to/your/example.png" with the actual path -->

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contribution](#Contribution)
- [Note](#Note)

## Introduction

The goal of this project is to showcase the integration of OpenAI's Whisper ASR model into Python applications, allowing for accurate and efficient speech-to-text conversion. By utilizing this code, you can easily leverage the power of OpenAI's Whisper to transcribe spoken content.

## Installation

1. Clone this repository to your local machine using:

   ```bash
   git clone https://github.com/perfect-everything/Speech-to-text_OpenAI_Whisper_Python.git
   ```
2. Install the required dependencies:

    ```bash
    pip install openai
    ```

## Usage

1. Obtain your [OpenAI API Keys](https://platform.openai.com/account/api-keys).
2. Replace `your_api_key` in `config.ini` with your actual OpenAI API key.
3. Run the script:
    ```bash
    python main.py
    ```
    This script performs the speech-to-text conversion using the Whisper ASR model.

## Configuration

In the `config.ini` file, you can adjust various settings to tailor the behavior of the speech-to-text conversion according to your needs.

* `openai_api_key`: Your OpenAI API Key for invoking Whisper model. (e.g. sk-5x4W*****************************************Krs)

## Contribution
Feel free to contribute to this project by improving existing code, adding new features, or fixing issues. If you have any questions or suggestions, please create an issue or submit a pull request.

## Note

This repository is in early devlopment. Everything is unstable yet. Things will change rapidly.
