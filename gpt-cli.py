import argparse
import json
import os
import shutil
from datetime import datetime
from io import StringIO
from uuid import uuid4
import copy

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pandas import read_excel
from pypdf import PdfReader

from session_manager import SessionManager

CONFIGDIR = os.path.join(os.path.expanduser("~"), ".gpt", ".config")
CONFIGFILE = os.path.join(CONFIGDIR, "config.json")
CONFIGTEMP = os.path.join(os.getcwd(), "config.json")
SESSIONSDIR = os.path.join(os.path.expanduser("~"), ".gpt", "sessions")
MODELS: list[str] = [
    # GPT-4.1 family
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",

    # GPT-4o family
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-mini-search-preview",
    "gpt-4o-search-preview",
    "chatgpt-4o-latest",

    # GPT-4 Turbo
    "gpt-4-turbo",
    "gpt-4-turbo-preview",
    "gpt-4-0125-preview",
    "gpt-4-1106-preview",
    "gpt-4-0613",

    # GPT-3.5 family
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k",

    # Reasoning models
    "o1",
    "o1-mini",
    "o1-preview",
    "o3",
    "o3-mini",
    "o4-mini"
]
TXT_EXTENSIONS: list[str] = [
     'txt',
     'csv',
     'json',
     'xml',
     'html',
     'htm',
     'md',
     'ini',
     'log',
     'yaml',
     'yml',
     'py',
     'java',
     'js',
     'css',
     'tsv',
     'tex',
     'cfg',
     'bat',
     'sh',
     'rst',
     'scala'
 ]

class CLIApp:
    def __init__(self):
        pass

    def handle_input(self):
        pass

    def print_help(self):
        pass


class ChatGPT:
    def __init__(self):
        self.run: bool = True
        self.model: str
        self.instructions: str
        self.messages: list[dict[str, str]]
        self.attached_files: list[str] = []
        self.file_contents: str = ""
        self.load_defaults()
        self.uuid: str = str(uuid4())
        self.client: OpenAI = OpenAI()
        self.md_console: Console = Console()
        self.session_manager: SessionManager = SessionManager()
        self.prompt_history: InMemoryHistory = InMemoryHistory()
        self.load_prompt_history()
        self.prompt_session = PromptSession(
            history=self.prompt_history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True
        )

    @property
    def ps1(self) -> str:
        if len(self.attached_files) != 0:
            return "\033[1;32mchatgpt:{}\033[0m (files: {})\033[0;35m>\033[0m".format(self.model, ", ".join(self.attached_files))
        else:
            return "\033[1;32mchatgpt:{}\033[0m\033[0;35m>\033[0m".format(self.model)

    def clear(self):
        _ = os.system('clear')

    def load_prompt_history(self):
        self.prompt_history.append_string(":set history ")
        self.prompt_history.append_string(":set instructions ")
        self.prompt_history.append_string(":instructions")
        self.prompt_history.append_string(":models")
        self.prompt_history.append_string(":sessions")
        self.prompt_history.append_string(":set default model ")
        self.prompt_history.append_string(":set default history ")
        self.prompt_history.append_string(":set default instructions ")
        self.prompt_history.append_string(":load ")
        self.prompt_history.append_string(":reset")
        self.prompt_history.append_string(":exit")
        self.prompt_history.append_string(":q")
        sessions = self.session_manager.get_session_list()
        for session in sessions:
            self.prompt_history.append_string(":load {}".format(session))
        self.prompt_history.append_string(":set model ")

    def load_defaults(self):
        if not os.path.exists(CONFIGDIR):
            os.makedirs(CONFIGDIR)
        if not os.path.isfile(CONFIGFILE):
            _ = shutil.copy(CONFIGTEMP, CONFIGFILE)
        with open(CONFIGFILE, 'r') as file:
            defaults: dict[str, str | dict[str, str] | bool] = json.load(file)
        self.model = defaults["model"]
        self.instructions = defaults["instructions"]
        self.messages = [defaults["messages"]]

    def set_defaults(self, option: str, value: str):
        with open(CONFIGFILE, 'r') as file:
            defaults: dict[str, str | dict[str, str] | bool] = json.load(file)
        match option:
            case "model":
                if value in MODELS: 
                    self.model = value
                    defaults["model"] = self.model
                else:
                    print("\ninvalid argument for \'model\', see :models for valid models")
            case "instruction":
                self.instructions = value
                self.messages = [{"role": "developer", "content": value}]
                defaults["messages"] = {"role": "developer", "content": value}
                defaults["instructions"] = self.instructions
            case _:
                print("\ninvalid default option, defaults not changed")
                self.help()
                return
        with open(CONFIGFILE, 'w') as file:
            json.dump(defaults, file)

    def stream_response_history(self, input: str):
        if self.file_contents != "":
            self.messages.append({"role": "user", "content": "{}, files: {{ {} }}".format(input,self.file_contents)})
            self.file_contents = ""
            self.attached_files = []
        self.messages.append({"role": "user", "content": "{}".format(input)})
        try:
            with Live(Markdown(""), console=self.md_console, refresh_per_second=8) as live:
                content_buffer: str = ""
                for chunk in self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    stream=True):

                    content: str = chunk.choices[0].delta.content
                    if content:
                        content_buffer += content
                    live.update(Markdown(content_buffer))
            self.messages.append({"role": "assistant", "content": content_buffer})
        except Exception as e:
            print(e)

    def parse_input(self):
        usr_input = self.prompt_session.prompt(ANSI(self.ps1))
        print()
        if len(usr_input) < 1:
            pass
        elif usr_input[0] == ":":
            cmd = usr_input.split(" ")[0].strip(":")
            match cmd:
                case "clear":
                    self.clear()
                case "models":
                    self.disp_models()
                case "set":
                    args = usr_input.split(" ")
                    if len(args) > 4:
                        print("\ntoo many arguments!")
                        self.help()
                    elif len(args) < 3:
                        print("\ntoo little arguments!")
                        self.help()
                    match args[1]:
                        case "model":
                            if args[2] in MODELS:
                                self.model = args[2]
                            else:
                                print("invalid model! enter a valid model:")
                                self.disp_models()
                        case "instructions":
                            pass
                        case "default":
                            usr_input = input("setting a default resets current session. continue? [Y/N] ")
                            if usr_input == "Y":
                                self.set_defaults(args[2], args[3])
                            else: 
                                print("\ndefaults not saved!")
                        case _:
                            print("\nnot a valid argument!")
                            self.help()
                case "instructions":
                    print("current instructions: {}".format(self.instructions))
                case "sessions":
                    sessions = self.session_manager.get_session_list()
                    for session in sessions:
                        print("\t{}".format(session))
                    print()
                case "load":
                    if len(usr_input.split(" ")) == 2:
                        session = usr_input.split(" ")[1]
                        messages = self.session_manager.load_session(session)
                        if messages != None:
                            self.messages = messages
                        else:
                            print("loading session failed")
                    else:
                        print("invalid argument!")
                        self.help()
                case "attach":
                    self.attach_file(usr_input[8:])
                case "remove":
                    self.remove_files()
                case "reset": 
                    save = input("want to save current session in file? [Y/N] ")
                    if save == "Y":
                        self.session_manager.save_session(self.messages, self.generate_session_name())
                        self.prompt_history.append_string(":load {}".format(self.generate_session_name()))
                    self.load_defaults()
                    self.help()
                case "exit" | "q":
                    save = input("want to save current session in file? [Y/N] ")
                    if save == "Y":
                        self.session_manager.save_session(self.messages, self.generate_session_name())
                    self.run = False
                case _:
                    print("\nnot a valid command!")
                    self.help()
        else:
            self.stream_response_history(usr_input)

    def disp_models(self):
        for i, model in enumerate(MODELS):
            if (i + 1) % 3 == 0:
                print("{:30}".format(model))
            else:
                print("{:30}".format(model), end="")
        print()

    def generate_session_name(self) -> str:
        topic_msg = self.messages.copy()
        topic_msg.append({"role": "user", "content": "generate a file name that would describe this session the best, at most 50 characters and only text and use only _ or - characters between words. NOTE! Only output the session topic nothing else! (no extensions)"})
        timestring = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=topic_msg)

            topic = completion.choices[0].message.content
            filename = "{}_{}".format(timestring, topic)
        except Exception as e:
            filename = "{}_no-topic".format(timestring)
            print("error! failed generating topic for session:\n {}".format(e))
            print("saving as {}".format(filename))

        return filename

    def help(self):
        print("ChatGPT CLI Interface, type a prompt or command\n")
        print("\tmodel:\t{}\n".format(self.model))
        print("\t:models\t\t\t\t\t\t--shows all available models")
        print("\t:sessions\t\t\t\t\t--lists all saved sessions")
        print("\t:instructions\t\t\t\t\t--shows current instrucions\n")
        print("\t:set model <model>\t\t\t\t--sets session model (gpt-4, o3, ...)")
        print("\t:set instructions <instructions>\t\t--sets session instructions (\"You're a helpful assistant\")")
        print("\t:load <session>\t\t\t\t\t--loads session history, see :sessions for saved sessions\n")
        print("\t:set default model <model>\t\t\t--sets default model")
        print("\t:set default history <on/off>\t\t\t--sets default history on/off")
        print("\t:set default instructions <instructions>\t--sets default instructions")
        print("\t:reset\t\t\t\t\t\t--resets current session history and loads defaults")
        print("\t:exit,\t:q\t\t\t\t\t--exits the interface")

    def remove_files(self):
        self.file_contents = ""
        self.attached_files = []

    def attach_file(self, path: str):
        if os.path.isfile(path):
            filename = path.split("/")[-1]
            extension = filename.split(".")[-1]
            if extension in TXT_EXTENSIONS:
                with open(path, 'r') as file:
                    content = file.read()
            elif extension == "xlsx":
                content = self.convert_xlsx_to_txt(path)
            elif extension == "pdf":
                content = self.convert_pdf_to_txt(path)
            else:
                content = ""
            self.attached_files.append(filename)
            self.file_contents += "{{ {} }}: {{ {} }}, ".format(filename, content)
        else:
            print("provided file path is invalid!")

    def convert_xlsx_to_txt(self, path: str) -> str:
        df = read_excel(path)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()

    def convert_pdf_to_txt(self, path: str) -> str:
        reader = PdfReader(path)
        content = ''
        for page in reader.pages:
            content += page.extract_text() or ''

        return content

def main(model: str):
    gpt = ChatGPT()
    gpt.help()

    while gpt.run:
        gpt.parse_input()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChatGPT CLI interface")
    _ = parser.add_argument("--model", type=str, default="", help="select model (gpt-4, o3, etc..)")
    args = parser.parse_args()
    main(args.model)
