import sys
import functools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import *
import os.path
from pathlib import Path
import web_gui2

class MenuBar(web_gui2.BrowserWindow):
    def __init__(self):
        super().__init__()
    def initMenuBar(self):
        #Add the menu bar
        #Taken from:  https://pythonprogramming.net/menubar-pyqt-tutorial/
        closeAction = QAction("Close window", self)
        closeAction.setShortcut("Ctrl+W")
        closeAction.setStatusTip("Leave the app")
        closeAction.triggered.connect(self.close_application)

        newTabAction = QAction("New tab", self)
        newTabAction.setShortcut("Ctrl+T")
        newTabAction.setStatusTip("Add a new tab")
        newTabAction.triggered.connect(self.add_tab)

        closeTabAction = QAction("Close tab", self)
        closeTabAction.setShortcut("Ctrl+Shift+T")
        closeTabAction.setStatusTip("Close current tab")
        closeTabAction.triggered.connect(self.close_tab)

        refreshPageAction = QAction("Refresh Webpage", self)
        refreshPageAction.setShortcut("Ctrl+R")
        refreshPageAction.setStatusTip("Refresh the current Webpage")
        refreshPageAction.triggered.connect(self.refresh_page)

        addBookmarkAction = QAction("Add or remove bookmark", self)
        addBookmarkAction.setShortcut("Ctrl+Shift+B")
        addBookmarkAction.setStatusTip("Add or remove a bookmark")

        removeHistoryAction = QAction("Clear current history", self)
        removeHistoryAction.setStatusTip("Clear history of web pages visited")

        copyAction = QAction("Copy", self)
        copyAction.setShortcut("Ctrl+C")
        copyAction.setStatusTip("Copy the selected text")
        copyAction.triggered.connect(self.copy)

        cutAction = QAction("Cut", self)
        cutAction.setShortcut("Ctrl+X")
        cutAction.setStatusTip("Cut the selected text")
        cutAction.triggered.connect(self.cut)

        pasteAction = QAction("Paste", self)
        pasteAction.setShortcut("Ctrl+V")
        pasteAction.setStatusTip("Paste previously copied text")
        pasteAction.triggered.connect(self.paste)

        setStartPageAction = QAction("Set Start page", self)
        setStartPageAction.setShortcut("Ctrl+Shift+S")
        setStartPageAction.setStatusTip("Set current page as your Start Page")
        setStartPageAction.triggered.connect(lambda: self.set_start_page())

        mainMenu = QMenuBar(self)
        fileMenu = mainMenu.addMenu("File")
        fileMenu.addAction(closeAction)
        fileMenu.addAction(newTabAction)
        fileMenu.addAction(closeTabAction)
        fileMenu.addAction(refreshPageAction)
        editMenu = mainMenu.addMenu("Edit")
        editMenu.addAction(copyAction)
        editMenu.addAction(cutAction)
        editMenu.addAction(pasteAction)
        self.historyMenu = mainMenu.addMenu("History")
        self.historyMenu.addAction(removeHistoryAction)
        self.bookmarksMenu = mainMenu.addMenu("Bookmarks")
        self.bookmarksMenu.addAction(addBookmarkAction)
        startPageMenu = mainMenu.addMenu("Start Page")
        startPageMenu.addAction(setStartPageAction)

        mainMenu.show()

