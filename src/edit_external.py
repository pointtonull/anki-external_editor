import io
import os
import tempfile
import subprocess
import sys

from aqt import mw

from .utils import is_executable, find_executable


def get_editor():
    user_choice = gc("editor")
    if is_executable(user_choice):
        return user_choice
    editors = [
        user_choice,
        user_choice + ".exe",
        "notepad++.exe",
        "notepad.exe",
        "code --wait",
        "gvim -f",
        "vim -gf",
        "atom",
        "atom.exe",
        "gedit",
    ]
    if sys.platform == "darwin":
        editors.append("open -t")
    for editor in editors:
        command = find_executable(editor)
        if command:
            return command

    raise RuntimeError("Could not find external editor")


def edit(text, ext):
    editor = get_editor()
    filename = tempfile.mktemp(suffix=ext)

    with io.open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

    cmd_list = editor.split() + [filename]
    proc = subprocess.Popen(cmd_list, close_fds=True)
    proc.communicate()

    with io.open(filename, 'r', encoding='utf-8') as file:
        return file.read()
