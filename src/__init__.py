import io
import os
import tempfile
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .utils import is_executable, find_executable
try:
    import aqt
    from aqt import mw
    BUILTIN_EDITOR = aqt.editor.Editor._onHtmlEdit
except ImportError:
    BUILTIN_EDITOR = None


def get_editor():
    config = mw.addonManager.getConfig(__name__)
    user_choice = config.get("editor")
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


class UpdateNoteHandler(FileSystemEventHandler):
    def __init__(self, state, field, filename):
        self.state = state
        self.field = field
        self.filename = filename

    def on_modified(self, _):
        with io.open(self.filename, 'r', encoding='utf-8') as file:
            text = file.read()

        self.state.note.fields[self.field] = text
        if not self.state.addMode:
            self.state.note.flush()
        self.state.loadNote(focusTo=self.field)

def edit(text, state, field):
    editor = get_editor()
    filename = tempfile.mktemp(suffix=".html")

    with io.open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

    observer = Observer()
    observer.schedule(UpdateNoteHandler(state, field, filename), filename)
    observer.start()

    cmd_list = editor.split() + [filename]
    proc = subprocess.Popen(cmd_list, close_fds=True)
    proc.communicate()

    observer.stop()
    observer.join()

    with io.open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def edit_with_external_editor(self, field):
    text = self.note.fields[field]
    try:
        text = edit(text, self, field)
        self.note.fields[field] = text
        if not self.addMode:
            self.note.flush()
        self.loadNote(focusTo=field)
    except RuntimeError:
        return BUILTIN_EDITOR(self, field)


if BUILTIN_EDITOR:
    aqt.editor.Editor._onHtmlEdit = edit_with_external_editor
