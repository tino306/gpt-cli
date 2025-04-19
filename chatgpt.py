import argparse
import os

import openai


def main():
    pass


if __name__ == "main":
    parser = argparse.ArgumentParser(description="ChatGPT CLI interface")
    _ = parser.add_argument("--model", type=str, default="gpt-4", help="Select ChatGPT model to use (gpt-4, gpt-03-mini-high, etc..)")
    args = parser.parse_args()
    main()
