#!/usr/local/bin/python3
from os.path import exists, abspath
from sys import argv
import json
import os
def cleanup(input_file, output_file) -> None:
    # Öffne den Index.
    input_path = abspath(input_file)
    output_path = abspath(output_file)

    if not exists(input_path):
        raise "input file not found"

    if exists(output_path):
        os.remove(output_path)

    with open(input_path, "r") as f:
        input_lines = f.readlines()
    seen = set()
    with open(output_path, "a+") as f:
        for line in input_lines:
            url = json.loads(line)["url"]
            if url not in seen:
                print(url)
                f.write(line)
                seen.add(url)


def main():
    input_file, output_file = argv[1], argv[2]
    cleanup(input_file, output_file)

if __name__ == "__main__":
    main()