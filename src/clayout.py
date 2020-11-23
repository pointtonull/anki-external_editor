from anki.hooks import wrap
from aqt.clayout import CardLayout
from aqt.qt import (
    QCursor,
    Qt,
)
from aqt.utils import tooltip

from .edit_external import edit
from .utils import pointversion


def editExternal(self, box, tedit):
    text = tedit.toPlainText()
    if box == "css":
        ext = ".css"
    else:
        ext = ".html"
    try:
        new = edit(text)
        tedit.setPlainText(new)
    except RuntimeError:
        tooltip('Error when trying to edit externally')
        return
CardLayout.editExternal = editExternal


if pointversion < 27:
    def common_context_menu(self, tedit, boxname):
        menu = tedit.createStandardContextMenu()
        c = menu.addAction("edit in external text editor")
        c.triggered.connect(lambda _, s=self: editExternal(s, boxname, tedit))
        return menu
    CardLayout.common_context_menu = common_context_menu


    def make_context_menu_front(self, location):
        menu = self.common_context_menu(self.tform.front, "front")
        menu.exec_(QCursor.pos())
    CardLayout.make_context_menu_front = make_context_menu_front


    def make_context_menu_css(self, location):
        menu = self.common_context_menu(self.tform.css, "css")
        menu.exec_(QCursor.pos())
    CardLayout.make_context_menu_css = make_context_menu_css


    def make_context_menu_back(self, location):
        menu = self.common_context_menu(self.tform.back, "back")
        menu.exec_(QCursor.pos())
    CardLayout.make_context_menu_back = make_context_menu_back


    def additional_clayout_setup(self):
        # https://stackoverflow.com/a/44770024
        self.tform.front.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tform.front.customContextMenuRequested.connect(self.make_context_menu_front)
        self.tform.css.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tform.css.customContextMenuRequested.connect(self.make_context_menu_css)
        self.tform.back.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tform.back.customContextMenuRequested.connect(self.make_context_menu_back)
    CardLayout.setupMainArea = wrap(CardLayout.setupMainArea, additional_clayout_setup)



if pointversion >= 28:
    def make_new_context_menu(self, location):
        if self.tform.front_button.isChecked():
            boxname = "front"
        elif self.tform.back_button.isChecked():
            boxname = "back"
        else:
            boxname = "css"
        tedit = self.tform.edit_area
        menu = tedit.createStandardContextMenu()
        c = menu.addAction("edit in external text editor")
        c.triggered.connect(lambda _, s=self: editExternal(s, boxname, tedit))
        menu.exec_(QCursor.pos())
    CardLayout.make_new_context_menu = make_new_context_menu


    def additional_clayout_setup(self):
        # https://stackoverflow.com/a/44770024
        self.tform.edit_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tform.edit_area.customContextMenuRequested.connect(self.make_new_context_menu)
    CardLayout.setup_edit_area = wrap(CardLayout.setup_edit_area, additional_clayout_setup)
