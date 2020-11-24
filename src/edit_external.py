from datetime import datetime
import io
import os
from pathlib import Path
import tempfile
import subprocess
import sys

from aqt import mw

from .config import gc
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


def edit(text, ext, named=False):
    editor = get_editor()
    if named and named [0] == "clayout":
        # some users might want to have a history of all versions of their templates.
        # For those the most discoverable/stable order would probably be: 
        #   profilename/modelid__modelname/{Front|Back|Css}
        # The easiest solution seems to add a config option to store the files
        # created for each external edit.
        # note to self : VSCode's "Local History" extension only shows prior versions for files
        # of the same name, so it doesn't work if the filename has a stimestamp in it.
        tvf = gc("template_versions_folder")
        if tvf:
            basefolder = tvf
        else:
            basefolder = tempfile.gettempdir()
        mid_name = f"{named[1]}__{named[2]}"
        folder = os.path.join(basefolder, mw.pm.name, mid_name, named[3])
        Path(folder).mkdir(parents=True, exist_ok=True)
        now = datetime.now().strftime('%Y-%m-%d__%H-%M-%S')  # ":" is not allowed in ntfs
        filename = os.path.join(folder, now + ext)
    else:
        filename = tempfile.mktemp(suffix=ext)

    with io.open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

    cmd_list = editor.split() + [filename]
    proc = subprocess.Popen(cmd_list, close_fds=True)
    proc.communicate()

    with io.open(filename, 'r', encoding='utf-8') as file:
        return file.read()
