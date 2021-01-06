# -*- coding: utf-8 -*-
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

# Import method to parse
from get_url import parse_site
#from PyQt5.QtWebChannel import QWebChannel
#from PyQt4.QtWebKit import QWebView#need to install PyQt4 which has to be built from source (yuck)
import socket#Taken from:  https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts
import pyperclip #install from https://pypi.python.org/pypi/pyperclip


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
        
        #Luke Douville's edit
        fl = open("website_elements.txt", "w")
        fl.write(str(website_elements))
        fl.close()
        global website_elements_refresh
        website_elements_refresh = website_elements
        
        if website_elements:
            for (htmlType, web_element) in website_elements:
                new_label = QLabel()
                print("\n\nhtmlType = ", htmlType)
                print("\n\n")
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
                # CSS
                elif (htmlType == 'css'):
                    #display the contents of the page in accordance with CSS properties
                    print("\n\n--------------------------\nCSS found!\n-------------------------------------")
                
                        #If the CSS says anything about the display
                        #Massive for loop?
                        #                        for i in range(0, len(web_element)):
                        #                        if web_element.startswith("background-color", i, len(web_element)):
                    if "background-color:" in web_element:
                        index = web_element.find("background-color:") + 17#place the index right after the text
                        color = ""
                        tempString = ""
                        for n in range(index, len(web_element)):
                            if n < web_element.find(" ", index, len(web_element)):
                                tempString += web_element[n]
                        color += re.findall('[a-z]', web_element[index:web_element.find(";", index, len(web_element) - 1)])
                        #color += tempString
                        print("\n\n----------------------------\nColor: ", color)
                        print("----------------------------------")
                        for n in range(0, len(color)):
                            if color[n] == "#":
                                continue
                            if color[n] == "f" or color[n] == "F":
                                #f is max value, so deepest red/green/blue possible
                                #fff is pure black
                                #000 is pure white
                                if n == 0:
                                    red = 255
                                elif n == 1:
                                    green = 255
                                elif n == 2:
                                    blue = 255
                elif (htmlType == 'style'):
                    #display the contents of the page in accordance with CSS properties
                    print("\n\n--------------------------\nstyle found!\n-----------------------------------")
                    continue
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
    #            file_to_open = open("websiteOutput.txt", "r")
    #            print(file_to_open.read())
    #            if website_elements_refresh:
    #                for (htmlType, web_element) in website_elements_refresh:
    #                    new_label = QLabel()
    #                    # Links
    #                    if (htmlType == 'a'):
    #                        if str(web_element[0]).strip() == "":
    #                            new_label.setText(str(web_element[1]))
    #                        else:
    #                            # Get the first element of the tuple which is the text to display for the link
    #                            new_label.setText(str(web_element[0]))
    #
    #                        new_label.setStyleSheet('color: blue') # Links are set to have blue text
    #                        new_label.setFont(QFont("Times", self.font_size, QFont.Normal)) # changes the font size
    #
    #                        new_label.mousePressEvent = functools.partial(self.link_clicked, source_object=new_label, url_text=web_element[1])
    #                    # Titles
    #                    elif (htmlType == 'title'):
    #                        self.tab_title = str(web_element) # Resets the title of the web page
    #                        new_label.setText(str(web_element))
    #                        title_font = QFont("Times", self.title_font_size, QFont.Bold)
    #                        new_label.setFont(title_font)
    #                    # Images
    #                    elif (htmlType == 'img'):
    #                        # web_elements contains (img_url)
    #                        new_img = self.store_img(str(url), str(web_element[0]))
    #                        if new_img == None:
    #                            new_label.setText(web_element[1])
    #                        else:
    #                            pixmap = QPixmap("Images/" + new_img)
    #                            new_label.setPixmap(pixmap)
    #                    # CSS
    #                    elif (htmlType == 'css'):
    #                        #display the contents of the page in accordance with CSS properties
    #                        continue
    #                    else:
    #                        new_label.setText(str(web_element))
    #
    #                    # Add the resulting element to the GUI
    #                    self.scroll_layout.addWidget(new_label)
    #
    #            file_to_open.close()
        self.register_address(self.current_url, font_size=18.0, title_font_size=19.0, back_forward_call = True)
    #        except Exception:
    #            print("\nUnable to refresh\n")
    #            print("website_elements_refresh: ", str(website_elements_refresh))
    #            print("\n")
    #            self.register_address(self.current_url)
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

