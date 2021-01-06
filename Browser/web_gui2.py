#-*- coding: utf-8 -*-
import sys
import functools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import *
import os.path
from pathlib import Path
import re
import MenuBar
import Tabs
import ParsingMethods

#Import method to parse
from get_url import parse_site
#from PyQt5.QtWebChannel import QWebChannel
#from PyQt4.QtWebKit import QWebView#need to install PyQt4 which has to be built from source (yuck)
import socket#Taken from:  https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts
import pyperclip #install from https://pypi.python.org/pypi/pyperclip

class BrowserWindow(QWidget):
    #In a Python class, the __init__ method must be called first
    def __init__(self):
        self.startPage = ""
        self.historyList = []
        self.bookmarkList = []

        #Initialize GUI
        self.initGUI()

    def initGUI(self):
        #Is the MenuBar class already instantiated by importing it?
        mb = MenuBar.MenuBar()#Instantiating the class will execute the __init__ method

        #Widget to hold all of our tabs
        self.tabs = QTabWidget()

        #Adds option to navigate to start page from the toolbar
        goToStartPageAction = startPageMenu.addAction("Visit start page")
        goToStartPageAction.triggered.connect(lambda: self.tabs.currentWidget().register_address(self.start_page))

        #When enter is pressed, pass the text in the address bar (url) to register_address
        addBookmarkAction.triggered.connect(lambda: self.tabs.currentWidget().add_or_remove_bookmark(self.tabs.currentWidget().address_bar.text()))

        #Action that removes all the url's from the history list
        removeHistoryAction.triggered.connect(lambda: self.clear_history())

        #The overarching layout of our GUI
        self.overall_layout = QVBoxLayout(self)

        t = Tabs();

        def refreshPage(self):
            try:
                self.registerAddress(self.currentURL)
            except:
                self.display_error("Unable to refresh page...")

    #Method to set a Start Page to execute upon startup
    def setStartPage(self):
        #If there is no url that's loaded in the tab, return
        if not self.tabs.currentWidget().current_url:
            return
        #Resets the start page to be the current url in the selected tab
        self.start_page = self.tabs.currentWidget().current_url
    
    #Adds the specified url to be bookmarked to the bookmarksMenu as an action
    def addBookmarkAction(self):
        bookmarkedURL = self.tabs.currentWidget().current_url #get the url being bookmarked
        #Make it an action
        action = self.bookmarksMenu.addAction(bookmarkedURL)
        action.triggered.connect(lambda: self.tabs.currentWidget().registerAddress(bookmarked_url))
    
    #Removes the specified url from the bookmarksMenu
    def remove_bookmark_action(self):
        #Goes through every action
        for action in self.bookmarksMenu.actions():
            #Once it finds the desired bookmark action to delete, it removes it
            if action.text() == self.tabs.currentWidget().current_url:
                self.bookmarksMenu.removeAction(action)

    #Method that sets the history list to be empty
    def clear_history(self):
        self.history_list = []
        #Clears every action except for the option to clear history
        for action in self.historyMenu.actions():
            if action.text() != "Clear current history":
                self.historyMenu.removeAction(action)
                    
    def create_history_action(self, url):
        #Adds the url as an action in the taskbar history
        action = self.historyMenu.addAction(url)
        action.triggered.connect(lambda: self.tabs.currentWidget().register_address(url))
    
    #Method to close the application
    def close_application(self):
        sys.exit()
    
    #Method to copy the selected text
    def copy(self):
        s = ""
        #Copy the text to the user's computer's clipboard
        #Taken from: https://stackoverflow.com/questions/11063458/python-script-to-copy-text-to-clipboard
        return pyperclip.copy(s)
    
    def cut(self):
        s = ""
        pyperclip.copy(s)
        return s
    
    def paste(self):
        if pyperclip.is_available() == True:
            pyperclip.paste()

class TabWindow(BrowserWindow):
    def __init__(self):
        self.initTabGUI()
        self.initGUIImages()

    #Helper method to initialize elements of the tab-specific GUI.
    def initTabGUI(self):
        self.space = QVBoxLayout()
        self.v_box = QVBoxLayout() #The overarching vertical layout for a tab
        self.topRow = QHBoxLayout() #The top row layout for a tab
        self.scrollLayout = QVBoxLayout() #A layout for the window part of the GUI (adds scrolling capabilities)
        self.websiteLayout = QVBoxLayout() #Another vertical layout to display the Website content

        #Text to be displayed as the tab title
        #Set to new tab when no page is loaded, the URL when there's no title, or the URL title if there's one provided
        self.tabTitle = "New Tab" #Set to "New Tab" as default
        self.currentURL = "" #Holds the current URL that the tab is displaying
        #Two stacks for the forward and back buttons (stores URLs)
        self.backHistoryStack = []
        self.ForwardHistoryStack = []

        self.fontSize = 14.0
        self.titleFontSize = 20.0

        #The scroll area of the layout where content from a Website will be displayed
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        #GUI elements that go in our top row
        self.backButton = QPushButton()
        self.forwardButton = QPushButton()
        self.HomeButton = QPushButton()
        self.addressBar = QLineEdit()
        self.goButton = QPushButton("Go!")
        self.refreshButton = QPushButton()
        self.zoomInButton = QPushButton("+")
        self.zoomOutButton = QPushButton("-")
        self.bookmarkButton = QPushButton()

        #Adds our top row elements to the top row
        self.topRow.addWidget(self.backButton)
        self.topRow.addWidget(self.forwardButton)
        self.topRow.addWidget(self.homeButton)
        self.topRow.addWidget(self.addressBar)
        self.topRow.addWidget(self.goButton)
        self.topRow.addWidget(self.refreshButton)
        self.topRow.addWidget(self.zoomInButton)
        self.topRow.addWidget(self.zoomOutButton)
        self.topRow.addWidget(self.bookmarkButton)

        #A nested vertical layout inside vBox (so we can add other widgets)
        self.space.addLayout(self.topRow)
        self.space.addLayout(self.websiteLayout)

        #Add the different layouts to the tab's top layout, vBox
        self.vBox.addLayout(self.space)
        self.vBox.addWidget(self.scrollArea)
        self.setLayout(self.vBox) #Sets vBox as the top layout for the tab

        #Events for the GUI
        self.addressBar.returnPressed.connect(lambda: self.registerAddress(self.addressBar.text(), self.fontSize, self.titleFontSize))
        self.goButton.clicked.connect(lambda: self.registerAddress(self.addressBar.text(), self.fontSize, self.titleFontSize))
        self.refreshButton.clicked.connect(lambda: self.refreshPage())
        self.backButton.clicked.connect(lambda: self.prevPage())
        self.forwardButton.clicked.connect(lambda: self.registerAddress(self.parent.startPage))
        self.zoomIn_button.clicked.connect(lambda: self.zoomOut())
        self.bookmarkButton.clicked.connect(lambda: self.addOrRemoveBookmark(self.addressBar.text()))

    #Method to add images to the GUI buttons
    def initGUIImages(self):
        #Sets image for back button
        backIcon = QIcon()
        backIcon.addPixmap(QPixmap("./Resources/BackIcon_512x512.PNG"))
        self.backButton.setIcon(backIcon)
        #Sets image for forward button
        forwardIcon = QIcon()
        forwardIcon.addPixmap(QPixmap("./Resources/ForwardIcon_512x512.PNG"))
        self.forwardButton.setIcon(forwardIcon)
        #Sets image for refresh button
        refreshIcon = QIcon()
        refreshIcon.addPixmap(QPixmap("./Resources/refreshIcon_128x128.PNG"))
        self.refreshButton.setIcon(refreshIcon)
        #Sets image for bookmark button
        self.bookmarkIcon = QIcon()
        self.bookmarkIcon.addPixmap(QPixmap("./Resources/bookmarkIcon_1600x1600.PNG"))
        self.bookmarkButton.setIcon(self.bookmarkIcon)
        #Sets image for the Home button
        self.homeIcon = QIcon()
        self.homeIcon.addPixmap(QPixmap("./Resources/homeIcon_512x512.PNG"))
        self.homeButton.setIcon(self.homeIcon)

    #URL methods are in ParsingMethods.py

    #Method to zoom into the Webpage
    #How to implement:  continuously load the current browser display into an image that the user can zoom into
    #For reference:  https://stackoverflow.com/questions/29390155/what-exactly-changes-in-the-css-rendering-when-desktop-browsers-zoom-in-or-out
    #Also:  https://www.quirksmode.org/mobile/viewports.html
    #Essentially:  increase the number of CSS pixels (as opposed to device pixels)
    def zoom_in(self):
        windowDimensions = QDesktopWidget().screenGeometry()
        windowHeight = windowDimensions.height()
        windowHeight *= 1.25
        windowWidth = windowDimensions.width()
        windowWidth *= 1.25
        
        #For now, just make the text bigger
        self.font_size = (self.font_size + (self.font_size / 4))
        self.title_font_size = (self.title_font_size + (self.title_font_size / 4))
        self.register_address(self.address_bar.text(), self.font_size, self.title_font_size)
   
   #Method to zoom out of the Webpage
    def zoom_out(self):
        windowDimensions = QDesktopWidget().screenGeometry()
        windowHeight = windowDimensions.height()
        windowHeight *= 0.75
        windowWidth = windowDimensions.width()
        windowWidth *= 0.75
        
        #For now, just make the text smaller
        self.font_size = (self.font_size - (self.font_size / 4))
        self.title_font_size = (self.title_font_size - (self.title_font_size / 4))
        self.register_address(self.address_bar.text(), self.font_size, self.title_font_size)

    #Helper method to create a widget that displays an error to the user (resets when new web page is loaded)
    def display_error(self, error_text):
        error_msg = QLabel() #Creates a new label to display the specified error
        error_msg.setText(error_text) #Sets the text for the error
        error_msg.setStyleSheet('color: red')
        self.website_layout.addWidget(error_msg)
    
    #Helper function to delete widgets inside another widget
    #from: https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
    def clear_layout(self, layout):
        while layout.count():
            child_widget = layout.takeAt(0)
            if child_widget.widget():
                child_widget.widget().deleteLater()

if __name__ == "__main__":
    #Create application loop
    app = QApplication(sys.argv)
    #Create instance of window widget
    a_window = BrowserWindow()
    a_window.show()
    #Keep application loop running
    sys.exit(ap.exec_())
