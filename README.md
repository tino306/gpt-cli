# GPT-CLI

A command-line interface for interacting with OpenAI's models.

## Features

-   Interactive chat with OpenAI models.
-   Session management to save and load conversations.
-   Attach files to your conversations.
-   Customizable instructions and model selection.
-   Command-based interface for managing the application.

## File Tree

```
.
├── config.json
├── gpt-cli.py
├── gpt-cli.sh
├── LICENSE
├── README.md
├── requirements.txt
└── session_manager.py
```

-   **`config.json`**: Configuration file for default model, instructions, and other settings.
-   **`gpt-cli.py`**: The main application file containing the CLI logic.
-   **`gpt-cli.sh`**: A shell script to easily run the application.
-   **`LICENSE`**: The license for the project.
-   **`README.md`**: This file.
-   **`requirements.txt`**: A list of python dependencies for this project.
-   **`session_manager.py`**: A helper module for managing chat sessions.

## Call Stack

The application starts by executing the `gpt-cli.sh` script. This script sets up the environment and runs the `gpt-cli.py` file.

The `gpt-cli.py` file initializes a `ChatGPT` object, which is the main class for the application. This class handles user input, sends requests to the OpenAI API, and displays the responses.

The `ChatGPT` class uses the `SessionManager` class to save and load chat sessions. The `SessionManager` class interacts with the file system to store session data.

## Getting Started

### Prerequisites

-   Python 3.6+
-   An OpenAI API key

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/tino306/gpt-cli.git
    ```
2.  Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3.  Set your OpenAI API key as an environment variable:
    ```sh
    export OPENAI_API_KEY="your-api-key"
    ```

### Usage

To start the application, run the following command:

```sh
./gpt-cli.sh
```

This will start the interactive chat interface. You can then type your prompts and press Enter to get a response from the AI.

### Commands

The application supports the following commands:

-   `:help`: Display the help message.
-   `:models`: List all available models.
-   `:sessions`: List all saved sessions.
-   `:instructions`: Show the current instructions.
-   `:set model <model>`: Set the model for the current session.
-   `:set instructions <instructions>`: Set the instructions for the current session.
-   `:load <session>`: Load a saved session.
-   `:set default model <model>`: Set the default model.
-   `:set default history <on/off>`: Set the default history on/off.
-   `:set default instructions <instructions>`: Set the default instructions.
-   `:reset`: Reset the current session.
-   `:exit` or `:q`: Exit the application.
-   `:attach <file_path>`: Attach a file to the conversation.
-   `:remove`: Remove all attached files.
-   `:clear`: Clear the terminal screen.