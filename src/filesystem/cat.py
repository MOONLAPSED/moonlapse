import os
import subprocess
import sys
import shutil
from typing import List
import os

def replace_text_in_file(fileName: str, old_content: str, newContent: str) -> None:
    """
    Replace text in a file with new content.

    Replace all occurrences of old_content with newContent in the file
    specified by fileName.

    :param fileName: The name of the file to modify.
    :type fileName: str
    :param old_content: The text to replace
    :type old_content: str
    :param newContent: The new content to replace old_content with
    :type newContent: str
    :return: None
    """
    with open(fileName, 'r') as file:
        content = file.read()

	# how many times old_content occurs in content
    count = content.count(old_content)
    # if count is not 1, then we can't replace the text
    if count != 1:
		# output error message to stderr and exit
        print(f"Error: {old_content} occurs {count} times in {fileName}.", file=sys.stderr)
        exit(-1)

	# replace old_content with new_content
    modified_content = content.replace(old_content, newContent)

    with open(fileName, 'w') as file:
        file.write(modified_content)

def create_or_replace_file(source: str, destination: str) -> None:
    """Create new file or replace existing file with new content."""
    try:
        if os.path.exists(destination):
            os.remove(destination)
        shutil.move(source, destination)
    except Exception:
        raise

def append_to_file(filename, content):
    """Appends strings to a file in Ubuntu, handling potential errors."""
    if not isinstance(content, list):
        content = [content]  # Treat single string input as a list

    with open(filename, 'a') as file:
        for line in content:
            file.write(line + '\n')

    print(f"Content appended to {filename}")

def load_file_content(file_name: str, start_line: int = 0, end_line: int = 1000) -> str:
    """
    Load content in file from start_line to end_line.
    If start_line and end_line are not provided, load the whole file.
    """
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
            if start_line < 0 or end_line <= start_line:
                sys.stderr.write("Error: start line must be greater than or equal to 0 and end line must be greater than start line.\n")
                sys.exit(1)
            content = "".join(lines[int(start_line):int(end_line)])
            if len(content.split('\n')) > 500:
                sys.stderr.write("Error: The content is too large, please set a reasonable reading range.\n")
                sys.exit(1)
            return content
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)


def get_project_tree() -> List[str]:
    """
    Get project files by "git ls-files" command

    :return: list of relative file paths of the project
    """
    try:
        output: List[str] = subprocess.check_output(["git", "ls-files"]).decode("utf-8").split("\n")
        if len(output) > 100:
            sys.stderr.write("Error: Too many files, you need to view the files and directory structure in each directory through the 'ls' command.\n")
            sys.exit(1)
        return output
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")


def main():
    home_dir = os.path.expanduser('~')  # Get user's home directory
    bashrc_path = os.path.join(home_dir, '.bashrc')

    # Strings to append (you can modify or get these from user input)
    strings_to_append = [
        'export OLLAMA_HOST=0.0.0.0',
        'export OLLAMA_ORIGINS=:127.0.0.1:11434',
        'export OLLAMA_PORT=11434',
        '# Custom alias',
        'alias lll="ls -alh"'
    ]

    append_to_file(bashrc_path, strings_to_append)

    # Making changes effective in the current session
    subprocess.run(["source", bashrc_path])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: cat.py <content file> <new file>", file=sys.stderr)
        sys.exit(1)

    content_file = sys.argv[1]
    new_file = sys.argv[2]
    create_or_replace_file(content_file, new_file)

    try:
        if len(sys.argv) == 4:
            file_name = sys.argv[1]
            old_content = sys.argv[2]
            new_content = sys.argv[3]

            replace_text_in_file(file_name, old_content, new_content)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(-1)

    main()
