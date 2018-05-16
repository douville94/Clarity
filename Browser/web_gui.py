# -*- coding: utf-8 -*-
import sys
import functools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import *
import os.path
from pathlib import Path
import re
import urllib3
import urllib.request

# Import method to parse
from get_url import parse_site
#from PyQt5.QtWebChannel import QWebChannel
#from PyQt4.QtWebKit import QWebView#need to install PyQt4 which has to be built from source (yuck)
#Next line taken from:  https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts
import socket
import pyperclip #install from https://pypi.python.org/pypi/pyperclip

# Our web browser class
#class BrowserWindow(QMainWindow):
class BrowserWindow(QWidget):
    # Initial Setup
    def __init__(self, parent):
        super(BrowserWindow, self).__init__(parent)

        # The default web page that tabs load (empty by default)
        self.start_page = ""
        self.history_list = []
        self.bookmark_list = []

        # Call method to initialize the GUI
        self.init_ui()

    # Initialize the GUI
    def init_ui(self):
        #Add the menu bar
        #Taken from:  https://pythonprogramming.net/menubar-pyqt-tutorial/
        closeAction = QAction("Close window", self)
        closeAction.setShortcut("Ctrl+W")
        closeAction.setStatusTip("Leave the app")
        closeAction.triggered.connect(self.close_application)
        #self.Qself.QMainWindow.statusBar()
        #Status bar doesn't seem to be working, maybe just leave it out
#        self.status = QStatusBar()
#        self.qWindow = QMainWindow(self)
#        self.qWindow.setStatusBar(self.status)

        newTabAction = QAction("New tab", self)
        newTabAction.setShortcut("Ctrl+T")
        newTabAction.setStatusTip("Add a new tab")
        newTabAction.triggered.connect(self.add_tab)

        closeTabAction = QAction("Close tab", self)
        closeTabAction.setShortcut("Ctrl+Shift+T")
        closeTabAction.setStatusTip("Close current tab")
        closeTabAction.triggered.connect(self.close_tab)

        addBookmarkAction = QAction("Add or remove bookmark", self)
        addBookmarkAction.setShortcut("Ctrl+Shift+B")
        addBookmarkAction.setStatusTip("Add or remove a bookmark")

        #viewBookmarksAction = QAction("View bookmarks", self)
        #viewBookmarksAction.setShortcut("Ctrl+B")
        #viewBookmarksAction.setStatusTip("View your currently saved bookmarks")
        #viewBookmarksAction.triggered.connect(self.viewBookmarks)
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

        #viewHistoryAction = QAction("View history", self)
        #viewHistoryAction.setShortcut("Ctrl+Shift+H")
        #viewHistoryAction.setStatusTip("View your history")
        #viewHistoryAction.triggered.connect(self.view_history)


        setStartPageAction = QAction("Set Start page", self)
        setStartPageAction.setShortcut("Ctrl+Shift+S")
        setStartPageAction.setStatusTip("Set current page as your Start Page")
        setStartPageAction.triggered.connect(lambda: self.set_start_page())

#        self.statusBar()
        mainMenu = QMenuBar(self)
        fileMenu = mainMenu.addMenu("File")
        fileMenu.addAction(closeAction)
        fileMenu.addAction(newTabAction)
        fileMenu.addAction(closeTabAction)
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

        # The widget to hold all of our tabs
        self.tabs = QTabWidget()

        # Adds the option to navigate to the start page from the toolbar
        goToStartPageAction = startPageMenu.addAction("Visit start page")
        goToStartPageAction.triggered.connect(lambda: self.tabs.currentWidget().register_address(self.start_page))

        # When enter is pressed, pass the text in the address bar (url) to register_address
        addBookmarkAction.triggered.connect(lambda: self.tabs.currentWidget().add_or_remove_bookmark(self.tabs.currentWidget().address_bar.text()))
        # Action that removes all the url's from the history list
        removeHistoryAction.triggered.connect(lambda: self.clear_history())

        # The overarching layout of our GUI
        self.overall_layout = QVBoxLayout(self)

        '''
        Tab Functionality
        '''
        # Button to add more tabs
        self.tab_button = QToolButton(self)
        self.tab_button.setText("+")
        font = self.tab_button.font()
        font.setBold(True)
        self.tab_button.setFont(font)
        # If the button is clicked, calls the method to create more tabs
        self.tab_button.clicked.connect(self.add_tab)
        # Adds the button to the tab widget
        self.tabs.setCornerWidget(self.tab_button, Qt.TopLeftCorner)
        # Adds the tab widget to the overall layout
        self.overall_layout.addWidget(self.tabs)
        self.overall_layout.insertSpacing(0, 30)

        # Creates the first tab instance on startup
        tab_1 = TabWindow(None, self)
        # Adds the tab to the Browser window
        self.tabs.addTab(tab_1, "New Tab")

        # Adds the ability to close tabs
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.check_if_last_tab)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        # Adds the ability to move the tabs
        self.tabs.setMovable(True)

        # Aesthetics of the tabs
        self.tabs.setTabShape(QTabWidget.Triangular)
        self.setLayout(self.overall_layout)

        # Sets the initial location and size of our window (xPos, yPos, width, height)
        self.setGeometry(50, 50, 1200, 700) # Set to 700 height due to taskbar in Windows
        self.setWindowTitle("Clarity") # title of window
        # The Window Icon (icon that shows up in top left part of window)
        window_icon = QIcon()
        window_icon.addPixmap(QPixmap("./Resources/PythonIcon_512x512.PNG"))
        self.setWindowIcon(window_icon)
        self.show() # display the window

    # Helper Method to create a new tab
    def add_tab(self):
        # Creates a tab instance
        tab = TabWindow(None, self)
        # Adds the tab
        self.tabs.addTab(tab, "New Tab")
        # Changes the current tab to be the new tab
        self.tabs.setCurrentWidget(tab)
        # If there is a start page set, have the new tab load it upon creation of the tab
        if self.start_page:
            tab.register_address(self.start_page)

    # Helper Method to alter the title of the current tab
    def update_tab_title(self):
        # Resets the title of the current tab based on the tab_title variable in the TabWindow
        self.tabs.setTabText(self.tabs.currentIndex(), self.tabs.currentWidget().tab_title)

    # Helper method to close the current tab
    def close_tab(self):
        # Close the current tab
        self.tabs.removeTab(self.tabs.currentIndex())
        # If there are no more tabs, close the application
        if not self.tabs:
            self.close_application()

    # Check if last tab available
    def check_if_last_tab(self):
        # If we're closing the last tab, close the entire application
        if self.tabs.count() <= 1:
            self.close_application()

    # Method to set a Start Page to execute upon startup
    def set_start_page(self):
        # If there is no url that's loaded in the tab, return
        if not self.tabs.currentWidget().current_url:
            return
        # Resets the start page to be the current url in the selected tab
        self.start_page = self.tabs.currentWidget().current_url

    # Adds the specified url to be bookmarked to the bookmarksMenu as an action
    def add_bookmark_action(self):
        bookmarked_url = self.tabs.currentWidget().current_url # get the url being bookmarked
        # Make it an action
        action = self.bookmarksMenu.addAction(bookmarked_url)
        action.triggered.connect(lambda: self.tabs.currentWidget().register_address(bookmarked_url))

    # Removes the specified url from the bookmarksMenu
    def remove_bookmark_action(self):
        # Goes through every action
        for action in self.bookmarksMenu.actions():
            # Once it finds the desired bookmark action to delete, it removes it
            if action.text() == self.tabs.currentWidget().current_url:
                self.bookmarksMenu.removeAction(action)

    # Method that sets the history list to be empty
    def clear_history(self):
        self.history_list = []
        # Clears every action except for the option to clear history
        for action in self.historyMenu.actions():
            if action.text() != "Clear current history":
                self.historyMenu.removeAction(action)

    def create_history_action(self, url):
            # Adds the url as an action in the taskbar history
            action = self.historyMenu.addAction(url)
            action.triggered.connect(lambda: self.tabs.currentWidget().register_address(url))

    # Method to close the application
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

# A class to represent an instance of a Tab
class TabWindow(QWidget):
    def __init__(self, parent, Browser):
        super(TabWindow, self).__init__(parent)
        # Call the method to initialize the tab specific GUI elements
        self.init_tab_GUI()
        # Call the method to initialize the images in the GUI
        self.init_GUI_images()
        # Variable to hold the parent Browser GUI for the tab
        self.parent = Browser

    # Helper method to initialize elements of the tab specific GUI
    def init_tab_GUI(self):
        self.space = QVBoxLayout()
        self.v_box = QVBoxLayout() # The overarching vertical layout for a tab
        self.top_row = QHBoxLayout() # The top row layout for a tab
        self.scroll_layout = QVBoxLayout() # A layout for the window part of the GUI (adds scrolling capabilities)
        self.website_layout = QVBoxLayout() # Another vertical layout to display website content

        # Text to be displayed as the tab title
        # (Set to new tab when no page is loaded, the url when there's no title, or the url title if there's one provided)
        self.tab_title = "New Tab" # set to 'New Tab' as default

        self.current_url = "" # Holds the current url that the tab is displaying
        # Two stacks for the forward and back buttons (stores urls)
        self.back_history_stack = []
        self.forward_history_stack = []

        self.font_size = 14.0
        self.title_font_size = 20.0

        # The scroll area of the layout where content from a website will be displayed
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        # GUI elements that go in our top row
        self.back_button = QPushButton()
        self.forward_button = QPushButton()
        self.home_button = QPushButton()
        self.address_bar = QLineEdit()
        self.go_button = QPushButton("Go!")
        self.refresh_button = QPushButton()
        self.zoomIn_button = QPushButton("+")
        self.zoomOut_button = QPushButton("--")
        self.bookmark_button = QPushButton()

        # Adds our top row elements to the top row
        self.top_row.addWidget(self.back_button)
        self.top_row.addWidget(self.forward_button)
        self.top_row.addWidget(self.home_button)
        self.top_row.addWidget(self.address_bar)
        self.top_row.addWidget(self.go_button)
        self.top_row.addWidget(self.refresh_button)
        self.top_row.addWidget(self.zoomIn_button)
        self.top_row.addWidget(self.zoomOut_button)
        self.top_row.addWidget(self.bookmark_button)

        # A nested vertical layout inside v_box (so we can add other widgets)
        self.space.addLayout(self.top_row)
        self.space.addLayout(self.website_layout)

        # Add the different layouts to the tab's top layout, v_box
        self.v_box.addLayout(self.space)
        self.v_box.addWidget(self.scroll_area)
        self.setLayout(self.v_box) # Sets v_box is the top layout for the tab

        # Events for the GUI
        self.address_bar.returnPressed.connect(lambda: self.register_address(self.address_bar.text(), self.font_size, self.title_font_size))
        self.go_button.clicked.connect(lambda: self.register_address(self.address_bar.text(), self.font_size, self.title_font_size))
        self.refresh_button.clicked.connect(lambda: self.refresh_page())
        self.back_button.clicked.connect(lambda: self.prev_page())
        self.forward_button.clicked.connect(lambda: self.forward_page())
        self.home_button.clicked.connect(lambda: self.register_address(self.parent.start_page))
        self.zoomIn_button.clicked.connect(lambda: self.zoom_in())
        self.zoomOut_button.clicked.connect(lambda: self.zoom_out())
        self.bookmark_button.clicked.connect(lambda: self.add_or_remove_bookmark(self.address_bar.text()))

    # Method to add images to the GUI buttons
    def init_GUI_images(self):
        # Sets image for back button
        back_icon = QIcon()
        back_icon.addPixmap(QPixmap("./Resources/BackIcon_512x512.PNG"))
        self.back_button.setIcon(back_icon)
        # Sets image for forward button
        forward_icon = QIcon()
        forward_icon.addPixmap(QPixmap("./Resources/ForwardIcon_512x512.PNG"))
        self.forward_button.setIcon(forward_icon)
        # Sets image for refresh button
        refreshIcon = QIcon()
        refreshIcon.addPixmap(QPixmap("./Resources/refreshIcon_128x128.PNG"))
        self.refresh_button.setIcon(refreshIcon)
        # Sets image for bookmark button
        self.bookmarkIcon = QIcon()
        self.bookmarkIcon.addPixmap(QPixmap("./Resources/bookmarkIcon_1600x1600.PNG"))
        self.bookmark_button.setIcon(self.bookmarkIcon)
        # Sets image for the Home button
        self.homeIcon = QIcon()
        self.homeIcon.addPixmap(QPixmap("./Resources/homeIcon_512x512.PNG"))
        self.home_button.setIcon(self.homeIcon)

    # Method to register the entered URL in the address bar
    def register_address(self, url, font_size=18.0, title_font_size=19.0, back_forward_call = False):
        # Clear the elements related to the previous website
        self.clear_layout(self.website_layout)
        self.clear_layout(self.scroll_layout)
        self.tab_title = url # resets the tab title to the url (later changes if an actual title is found)

        # If the url is empty, just return
        if url.strip() == "":
            return

        try:
            # Retrieve the data from the url and return the resulting info from parsing the data
            website_elements = parse_site(url)
            if website_elements:
                for (htmlType, web_element) in website_elements:
                    new_label = QLabel()
                    # Links
                    if (htmlType == 'a'):
                        if str(web_element[0]).strip() == "":
                            new_label.setText(str(web_element[1]))
                        else:
                            # Get the first element of the tuple which is the text to display for the link
                            new_label.setText(str(web_element[0]))

                        new_label.setStyleSheet('color: blue') # Links are set to have blue text
                        new_label.setFont(QFont("Times", self.font_size, QFont.Normal)) # changes the font size

                        new_label.mousePressEvent = functools.partial(self.link_clicked, source_object=new_label, url_text=web_element[1])
                    # Titles
                    elif (htmlType == 'title'):
                        self.tab_title = str(web_element) # Resets the title of the web page
                        new_label.setText(str(web_element))
                        title_font = QFont("Times", self.title_font_size, QFont.Bold)
                        new_label.setFont(title_font)
                    # Images
                    elif (htmlType == 'img'):
                        # web_elements contains (img_url)
                        new_img = self.store_img(str(url), str(web_element[0]))
                        if new_img == None:
                            new_label.setText(web_element[1])
                        else:
                            pixmap = QPixmap("Images/" + new_img)
                            new_label.setPixmap(pixmap)
                    else:
                        new_label.setText(str(web_element))

                    # Add the resulting element to the GUI
                    self.scroll_layout.addWidget(new_label)

        except Exception as e:
            # Display an error if there's an error while trying to access the website
            self.display_error("This site can't be reached.")

        # Add the URL to the global history list
        self.parent.history_list.append(url)
        # Call method to add urls in history to toolbar
        self.parent.create_history_action(url)

        # Call a method to update the tab title from the BrowserWindow class
        self.parent.update_tab_title()
        # Resets the address bar text to match the current url
        self.address_bar.setText(str(url))

        # Changes the image of the bookmark button based on whether the url is bookmarked
        if url in self.parent.bookmark_list:
            self.bookmarkIcon.addPixmap(QPixmap("./Resources/bookmarkFilledIcon_1600x1600.PNG"))
            self.bookmark_button.setIcon(self.bookmarkIcon)
        else:
            self.bookmarkIcon.addPixmap(QPixmap("./Resources/bookmarkIcon_1600x1600.PNG"))
            self.bookmark_button.setIcon(self.bookmarkIcon)

        # Only append to the back button stack if register_address isn't being called by the back button
        if not back_forward_call:
            # Empties the forward button stack
            self.forward_history_stack.clear()

            # If there was a previous url loaded by the tab, append it to the back button stack
            if not self.current_url.strip() == "":
                self.back_history_stack.append(self.current_url)

        # Resets the current url variable to be the url just loaded
        # (NOTE: keep below if not back_forward_call to avoid bug with back button)
        self.current_url = url

    # Helper method which adds link functionality
    # Takes the mouseClickEvent, the source object that was clicked, and the url as arguements
    def link_clicked(self, event, source_object=None, url_text="https://google.com"):
        try:
            # go to the specified URL
            self.register_address(url_text, self.font_size, self.title_font_size)
        # Throw an error if we can't access the site
        except Exception:
            self.display_error("The given link is not valid...")

    # Method that loads an image from source and stores it to our folder.
    def store_img(self, url, path):
        print("path: ", path)
        print("\n")
        #print ("\nTHE URL PASSED IN IS:", url)
        # make sure the url begins with https:// or http://
        if not url.startswith('http'):
            # make sure there's a www. at the beginning also.
            if not url.startswith('www.'):
                url = "www." + url
            url = "https://" + url
        # combine url and path depending on path and url format.
        if path.startswith('data:'):
            fin = str(path)
        elif path.startswith('http'):
            fin = str(path)
        elif path.startswith('//'):
            fin = "https:" + path
        elif path.startswith('/') or url.endswith('/'):
            fin = str(url + path)
        else:
            fin = str(url+'/'+path)

        print("fin: ", fin)
        print("\n")

        # determine name for new image file.
        name = ""
        for letter in path:
            if letter == '/':
                name = name + '_'
#                continue
            else:
                name = name + letter
            limit = re.match(r'(.{1,100})', name)
            name = limit.group(1)
        # if the image file already exists then just load it.
        file_path = Path("Images/" + name)
        if file_path.exists():
            return name
        # otherwise try to load the image.
        try:
            f = urllib.request.urlopen(fin)
        except:
            print("Could not load the combo of url:", url, "and path", path, " to form", fin, "\n")
            return None
        # write to a new file.
        cpy = open("Images/" + name, "wb")
        cpy.write(f.read())
        return name

    # Method to refresh the current page
    def refresh_page(self):
        try:
            self.register_address(self.current_url)
        except Exception:
            self.display_error("Unable to refresh the page...")

    # Method to go to the previous page in the history
    # If there is no previous page, it should not be clickable
    def prev_page(self):
        # If the stack for the back button is empty, do nothing and return
        if not self.back_history_stack:
            return
        # Place the current url on the forward button stack
        self.forward_history_stack.append(self.current_url)
        # Navigate back to the previous page
        self.register_address(self.back_history_stack.pop(), self.font_size, self.title_font_size, True)


    # Method to go to the next page in the history
    def forward_page(self):
        # If the stack for the forward button is empty, do nothing and return
        if not self.forward_history_stack:
            return
        # Place the current url on the back button stack
        self.back_history_stack.append(self.current_url)
        # Navigate to last page placed in the forward button stack
        self.register_address(self.forward_history_stack.pop(), self.font_size, self.title_font_size, True)

    # Method to add or remove a bookmark (adds it if it doesn't exist and removes it if it does)
    def add_or_remove_bookmark(self, url):
        # If there is no url, return
        if not url:
            return
        # If the bookmark exists, remove it. If the bookmark doesn't exist, add it
        if url in self.parent.bookmark_list:
            self.parent.bookmark_list.remove(url) # Remove the bookmark
            # Change the bookmark button's image to show url is bookmarked
            self.bookmarkIcon.addPixmap(QPixmap("./Resources/bookmarkIcon_1600x1600.PNG"))
            self.bookmark_button.setIcon(self.bookmarkIcon)
            self.parent.remove_bookmark_action()
        else:
            self.parent.bookmark_list.append(url) # Add the bookmark
            # Change the bookmark button's image to show url is bookmarked
            self.bookmarkIcon.addPixmap(QPixmap("./Resources/bookmarkFilledIcon_1600x1600.PNG"))
            self.bookmark_button.setIcon(self.bookmarkIcon)
            # Call method to add the bookmark to the toolbar
            self.parent.add_bookmark_action()

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

    # Helper method to create a widget that displays an error to the user (resets when new web page is loaded)
    def display_error(self, error_text):
        error_msg = QLabel() # Creates a new label to display the specified error
        error_msg.setText(error_text) # Sets the text for the error
        error_msg.setStyleSheet('color: red')
        self.website_layout.addWidget(error_msg)

    # Helper function to delete widgets inside another widget
    # from: https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
    def clear_layout(self, layout):
        while layout.count():
            child_widget = layout.takeAt(0)
            if child_widget.widget():
                child_widget.widget().deleteLater()

if __name__ == '__main__':
    # Create the application loop
    app = QApplication(sys.argv)
    # Create an instance of our window widget
    a_window = BrowserWindow(None)
    a_window.show()
    # Keep the application loop running
    sys.exit(app.exec_())
