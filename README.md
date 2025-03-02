# Chatbot Server

This project is a chatbot server built with Node.js and integrated with Ollama to provide intelligent chat capabilities. It is designed to work in conjunction with a chatbot client application.

## Features

* Provides an API for the chatbot client application to interact with the chatbot.
* Integrates with Ollama for processing chat requests.
* Intuitive web interface built with Streamlit.

## Installation

1.  **Requirements**:
    * Python (version 3.10)
    * conda (Miniconda or Anaconda)
    * pip (Python package installer)
    * Ollama (installed and configured)
2.  **Create conda environment**:

    ```bash
    conda create -n server-env python=3.10
    conda activate server-env
    ```
3.  **Install ffmpeg**:

    ```bash
    conda install conda-forge::ffmpeg
    ```
4.  **Install Python packages**:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Install Ollama**:
    * Ensure you have installed and configured Ollama according to the Ollama developer's instructions.
6.  **Run server**:

    ```bash
    python server.py
    ```
7.  **Run web interface**:

    ```bash
    streamlit run app.py
    ```

## Notes

* Ensure that Ollama is running before starting the chatbot server.
* You can customize the server settings in the `server.py` file.
* The `requirements.txt` file contains a list of required Python packages.
* The `app.py` file contains the source code for the web interface.