import argparse
import json
import os

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

DEFAULTSDIR = os.path.join(os.path.expanduser("~"), ".gpt", ".config", "defaults.json")
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

    def load_defaults(self):
        with open(DEFAULTSDIR, 'r') as file:
            defaults = json.load(file)
        self.model = defaults["model"]
        self.instructions = defaults["instructions"]
        self.messages = [defaults["messages"]]
        self.history = True if defaults["history"] else False

    def set_defaults(self, option: str, val: str):
        with open(DEFAULTSDIR, 'r') as file:
            defaults = json.load(file)
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
        with open(DEFAULTSDIR, 'w') as file:
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
                case "reset": 
                    self.load_defaults()
                    self.help()
                case "exit" | "q":
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

    def help(self):
        print("ChatGPT CLI Interface, type a prompt or command\n")
        print("\tmodel:\t{}\n".format(self.model))
        print("\t:models\t\t\t\t\t\t--shows all available models")
        print("\t:instructions\t\t\t\t\t--shows current instrucions\n")
        print("\t:set model <model>\t\t\t\t--sets session model (gpt-4, gpt-o3 ...)")
        print("\t:set instructions <instructions>\t\t--sets session instructions (\"You're a helpful assistant\")")
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
    _ = parser.add_argument("--model", type=str, default="", help="select model (gpt-4, gpt-o3, etc..)")
    args = parser.parse_args()
    main(args.model)
