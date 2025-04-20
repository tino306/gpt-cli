import argparse
import json
import os
import shutil
from datetime import datetime
import uuid

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

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


class ChatGPT:
    def __init__(self):
        self.model: str
        self.instructions: str
        self.messages: list[dict[str, str]]
        self.history: bool
        self.load_defaults()
        self.client: OpenAI = OpenAI()
        self.md_console: Console = Console()
        self.run: bool = True
        self.session_id: uuid.UUID = uuid.uuid4()

    def load_defaults(self):
        if not os.path.exists(CONFIGDIR):
            os.makedirs(CONFIGDIR)
        if not os.path.isfile(CONFIGFILE):
            shutil.copy(CONFIGTEMP, CONFIGFILE)
        with open(CONFIGFILE, 'r') as file:
            defaults: dict[str, str | dict[str, str] | bool] = json.load(file)
        self.model = defaults["model"]
        self.instructions = defaults["instructions"]
        self.messages = [defaults["messages"]]
        self.history = True if defaults["history"] else False

    def set_defaults(self, option: str, val: str):
        with open(CONFIGFILE, 'r') as file:
            defaults: dict[str, str | dict[str, str] | bool] = json.load(file)
        match option:
            case "model":
                if val in MODELS: 
                    self.model = val
                    defaults["model"] = self.model
                else:
                    print("\ninvalid argument for \'model\', see :models for valid models")
            case "instruction":
                self.instructions = val
                self.messages = [{"role": "developer", "content": val}]
                defaults["messages"] = {"role": "developer", "content": val}
                defaults["instructions"] = self.instructions
            case "history":
                match val:
                    case "on" | "ON" | "1":
                        self.history = True
                        defaults["history"] = self.history
                    case "off" | "OFF" | "0":
                        self.history = False
                        defaults["history"] = self.history
                    case _:
                        print("\ninvalid argument for 'history' (on/off)")
            case _:
                print("\ninvalid default option, defaults not changed")
                self.help()
                return
        with open(CONFIGFILE, 'w') as file:
            json.dump(defaults, file)

    def stream_response_history(self, input: str):
        self.messages.append({"role": "user", "content": input})
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages)

            md_out = Markdown(completion.choices[0].message.content)
            self.md_console.print(md_out)
        except Exception as e:
            print(e)

    def stream_response(self, input: str):
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=self.instructions,
                input=input)

            md_out = Markdown(response.output_text)
            self.md_console.print(md_out)
        except Exception as e:
            print(e)

    def parse_input(self):
        if self.history:
            ps1 = "\033[1;32mchatgpt:{}\033[0m (history=on)\033[0;35m>\033[0m".format(self.model)
        else: 
            ps1 = "\033[1;32mchatgpt:{}\033[0m (history=off)\033[0;35m>\033[0m".format(self.model)
        print(ps1, end=" ")
        usr_input = input("")
        print()
        if len(usr_input) < 1:
            pass
        elif usr_input[0] == ":":
            cmd = usr_input.split(" ")[0].strip(":")
            match cmd:
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
                        case "instructions":
                            pass
                        case "history":
                            match args[2]:
                                case "on" | "ON" | "1":
                                    self.history = True
                                case "off" | "OFF" | "0":
                                    self.history = False
                                case _:
                                    print("\nnot a valid argument!")
                                    self.help()
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
                    self.load_sessions()
                case "load":
                    if len(usr_input.split(" ")) == 2:
                        session = usr_input.split(" ")[1]
                        self.load_session(session)
                    else:
                        print("invalid argument!")
                        self.help()
                case "reset": 
                    self.load_defaults()
                    if self.history:
                        save = input("want to save current session in file? [Y/N] ")
                        if save == "Y":
                            self.save_session()
                    self.help()
                case "exit" | "q":
                    if self.history:
                        save = input("want to save current session in file? [Y/N] ")
                        if save == "Y":
                            self.save_session()
                    self.run = False
                case _:
                    print("\nnot a valid command!")
                    self.help()
        else:
            if self.history:
                self.stream_response_history(usr_input)
            else:
                self.stream_response(usr_input)

    def disp_models(self):
        for i, model in enumerate(MODELS):
            if (i + 1) % 3 == 0:
                print("{:30}".format(model))
            else:
                print("{:30}".format(model), end="")
        print()

    def generate_session_name(self) -> str:
        topic_msg = self.messages
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
            print("failed generatic session topic for filename:\n {}".format(e))
            print("saving as {}".format(filename))

        return filename

    def save_session(self):
        if not os.path.exists(SESSIONSDIR):
            os.makedirs(SESSIONSDIR)
        name = self.generate_session_name()
        sessionfile = os.path.join(SESSIONSDIR, name)
        with open(sessionfile, 'w') as file:
            json.dump(self.messages, file)
        print("session '{}' saved".format(name)) 

    def load_session(self, filename: str):
        sessionfile = os.path.join(SESSIONSDIR, filename)
        if os.path.isfile(sessionfile):
            with open(sessionfile, 'r') as file:
                self.messages = json.load(file)
            self.history = True
        else:
            print("invalid session filename '{}'\n".format(filename))
            self.load_sessions()

    def load_sessions(self):
        if not os.path.exists(SESSIONSDIR):
            os.makedirs(SESSIONSDIR)
        sessions = os.listdir(SESSIONSDIR)
        print("\tsaved sessions:")
        for session in sessions:
            print("\t{}".format(session))
        print()

    def help(self):
        print("ChatGPT CLI Interface, type a prompt or command\n")
        print("\tmodel:\t{}\n".format(self.model))
        print("\t:models\t\t\t\t\t\t--shows all available models")
        print("\t:sessions\t\t\t\t\t--lists all saved sessions")
        print("\t:instructions\t\t\t\t\t--shows current instrucions\n")
        print("\t:set model <model>\t\t\t\t--sets session model (gpt-4, o3, ...)")
        print("\t:set instructions <instructions>\t\t--sets session instructions (\"You're a helpful assistant\")")
        print("\t:set history <on/off>\t\t\t\t--sets session history (on/off)")
        print("\t:load <session>\t\t\t\t\t--loads session history, see :sessions for saved sessions\n")
        print("\t:set default model <model>\t\t\t--sets default model")
        print("\t:set default history <on/off>\t\t\t--sets default history on/off")
        print("\t:set default instructions <instructions>\t--sets default instructions")
        print("\t:reset\t\t\t\t\t\t--resets current session history and loads defaults")
        print("\t:exit,\t:q\t\t\t\t\t--exits the interface")

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
