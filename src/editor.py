try:
    import aqt
    BUILTIN_EDITOR = aqt.editor.Editor._onHtmlEdit
except ImportError:
    BUILTIN_EDITOR = None

from .edit_external import edit


def edit_with_external_editor(self, field):
    text = self.note.fields[field]
    try:
        text = edit(text, ".html")
        self.note.fields[field] = text
        if not self.addMode:
            self.note.flush()
        self.loadNote(focusTo=field)
    except RuntimeError:
        return BUILTIN_EDITOR(self, field)


if BUILTIN_EDITOR:
    aqt.editor.Editor._onHtmlEdit = edit_with_external_editor
