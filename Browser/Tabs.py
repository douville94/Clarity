import sys
import functools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import *
import os.path
from pathlib import Path

class Tabs():
    def __init__(self):
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
        tab_1 = TabWindow(self)
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
        tab = TabWindow(self)
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
