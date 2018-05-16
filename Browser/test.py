#!/usr/bin/python
# import parser
import urllib

from PyQt5.QtWidgets import *
import get_url
import web_gui
import web_parse
import time
import sys
import functools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import *
import sys


'''
Method tests for get_url byitself (not including the parser or GUI)
'''

# Methods to test whether get_url can sucessfully access a good url
def test_url_suceed():
	try:
		get_url.parse_site('http://pythonprogramming.net')
		assert True
	except Exception:
		assert False
def test_url_suceed_2():
	try:
		get_url.parse_site('https://google.com')
		assert True
	except Exception:
		assert False
# Test to see whether the same url test suceeds without the https:// attatchment
def test_url_suceed_without_full_url():
	try:
		get_url.parse_site('google.com')
		assert True
	except Exception:
		assert False
# Methods to see if get_url can handle a bad url without breaking
def test_bad_url():
	try:
		get_url.parse_site('I_like_WAFFles')
		assert False
	except Exception:
		assert True
# Misspelled url (asserts true if method throws error)
def test_bad_url_2():
	try:
		get_url.parse_site('http://gogle.com')
		assert False
	except Exception:
		assert True
# Incomplete url (asserts true if method throws error)
def test_bad_url_3():
	try:
		get_url.parse_site('http://google')
		assert False
	except Exception:
		assert True
# Empty url (asserts true if method throws error)
def test_bad_url_4():
	try:
		get_url.parse_site('')
		assert False
	except Exception:
		assert True

'''
Methods that test the GUI
'''

######### Tests for History features #########

# Tests whether the clear history method sucessfully clears the history list
def test_clear_history():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)

	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().register_address("bing.com")
	instance.clear_history()
	if len(instance.history_list) == 0:
		assert True
	else:
		assert False

# Method to test whether the loaded urls are properly stored in the history list
def test_add_history():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)

	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().register_address("google.com")
	if ("github.com" in instance.history_list) and ("google.com" in instance.history_list):
		assert True
	else:
		assert False

# Method to test whether the history list is shared amongst tabs
def test_history_multiple_tabs():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	# Load one website to add it to back history stack for the current tab
	instance.tabs.currentWidget().register_address("github.com")
	instance.add_tab() # create a second tab
	# Load url in the second tab
	instance.tabs.currentWidget().register_address("google.com")
	# urls loaded in both tabs should be added to history list
	if len(instance.history_list) == 2:
		assert True
	else:
		assert False

######### Tests for Start Page features #########
# Method to test whether the start page is sucessfully set to the current url in tab when set_start_page is called
def test_set_start_page():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)

	instance.tabs.currentWidget().register_address("google.com")
	instance.set_start_page()
	# Should have set the start page to the current url that's loaded in the selected tab
	if instance.start_page == "google.com":
		assert True
	else:
		assert False

# Same as the last method but tests whether it stores the correct url from the current tab (and not a different tab) for the start page
def test_set_start_page_in_new_tab():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)

	# Load a website in the default tab
	instance.tabs.currentWidget().register_address("google.com")
	instance.add_tab() # add a new tab (should switch to it as default)
	# Load a different website in the new tab
	instance.tabs.currentWidget().register_address("bing.com")
	instance.set_start_page() # call set_start_page

	# Should set the start page to the new tab's url, not the first tab's url
	if instance.start_page == "bing.com":
		assert True
	else:
		assert False

# Method to test whether new tabs open (by default) to the new start page
def test_new_tab_opens_start_page():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)

	instance.tabs.currentWidget().register_address("github.com")
	instance.set_start_page() # Set the start page to 'github.com'
	instance.add_tab()
	# The new tab should open 'github.com' since it is the selected start page
	if instance.tabs.currentWidget().current_url == "github.com":
		assert True
	else:
		assert False

######### Tests for Back Button #########
# Method to test if the stack for the back button stores the correct websites and places them in the right order
def test_back_button_stack():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)

	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().register_address("bing.com")
	instance.tabs.currentWidget().register_address("github.com")

	# Tests whether the first element is the first website searched and the second element is the second website searched
	if instance.tabs.currentWidget().back_history_stack[0] == "google.com" and instance.tabs.currentWidget().back_history_stack[1] == "bing.com":
		assert True
	else:
		assert False

# Method to test that the last website loaded into the tab is not appended to the back button stack yet
def test_back_button_stack_no_last_url():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().register_address("bing.com")

	# 'bing.com' is the current url so it shouldn't be part of the back button's stack yet (will get added when another website is loaded)
	if "bing.com" not in instance.tabs.currentWidget().back_history_stack:
		assert True
	else:
		assert False

# Method to test whether the back button stack remains seperate for each tab (doesn't append to tab's stack if url loaded on different tab)
def test_separate_back_button_stack_per_tab():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	# Load one website to add it to back history stack for the current tab
	instance.tabs.currentWidget().register_address("github.com")
	instance.add_tab() # create a second tab
	# Load url in the second tab
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.setCurrentIndex(0) # switch back to the first tab
	# If the url loaded in the second tab shows up in the back button stack for the first tab, assert False
	if "google.com" not in instance.tabs.currentWidget().back_history_stack:
		assert True
	else:
		assert False

# Test whether the prev_page function sucessfully goes back to last loaded url when called
def test_prev_page():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().prev_page()

	if instance.tabs.currentWidget().current_url == "github.com":
		assert True
	else:
		assert False

# Test whether the prev_page function correctly pops the last value in back button stack
def test_prev_page_back_button_stack():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().prev_page()

	# Back button stack should now be empty now that we naviaged back to 'github.com' with prev_page
	if len(instance.tabs.currentWidget().back_history_stack) == 0:
		assert True
	else:
		assert False

######### Tests for Forward Button #########
# Method to test whether the forward stack gets the urls stored correctly and in the right order
def test_forward_stack_contents():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().prev_page()
	instance.tabs.currentWidget().prev_page()

	if instance.tabs.currentWidget().forward_history_stack[0] == "github.com" and instance.tabs.currentWidget().forward_history_stack[1] == "google.com":
		assert True
	else:
		assert False

# Method to test whether the forward stack is emptied when a new url is loaded (not including sites loaded using back button)
def test_clear_forward_stack():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().prev_page()
	instance.tabs.currentWidget().prev_page()
	instance.tabs.currentWidget().register_address("https://atom.io")
	# Forward history stack should be emptied every time there's a new url that's loaded (except for the back button's calls to register_address)
	if len(instance.tabs.currentWidget().forward_history_stack) == 0:
		assert True
	else:
		assert False

# Method to test whether the forward_page method sucesfully loads the correct website
def test_forward_page():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().prev_page()
	instance.tabs.currentWidget().prev_page()
	instance.tabs.currentWidget().forward_page()
	instance.tabs.currentWidget().forward_page()
	if instance.tabs.currentWidget().current_url == "github.com":
		assert True
	else:
		assert False

######### Tests for Bookmark Features #########
# Method to test whether a bookmark can be added
def test_add_bookmark():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	instance.tabs.currentWidget().add_or_remove_bookmark(instance.tabs.currentWidget().current_url)
	if "github.com" in instance.bookmark_list:
		assert True
	else:
		assert False

# Method that tests if we try to bookmark an url that is already bookmarked, we remove the url
def test_remove_bookmark():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	# First time adds the bookmark
	instance.tabs.currentWidget().add_or_remove_bookmark(instance.tabs.currentWidget().current_url)
	# Second time it detects the bookmark is already there so it removes it
	instance.tabs.currentWidget().add_or_remove_bookmark(instance.tabs.currentWidget().current_url)
	if "github.com" not in instance.bookmark_list:
		assert True
	else:
		assert False

# Method to test whether the bookmark list is shared amongst tabs
def test_add_bookmarks_multi_tabs():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	# First time adds the bookmark
	instance.tabs.currentWidget().add_or_remove_bookmark(instance.tabs.currentWidget().current_url)
	instance.add_tab() # Adds a tab and sets it as current tab
	instance.tabs.currentWidget().register_address("google.com")
	instance.tabs.currentWidget().add_or_remove_bookmark(instance.tabs.currentWidget().current_url)
	if "github.com" in instance.bookmark_list and "google.com" in instance.bookmark_list:
		assert True
	else:
		assert False

# Method to test whehter another tab is able to recognize whether a website is bookmarked or not
def test_add_bookmarks_multi_tabs_2():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("github.com")
	# First time adds the bookmark
	instance.tabs.currentWidget().add_or_remove_bookmark(instance.tabs.currentWidget().current_url)
	instance.add_tab() # Adds a tab and sets it as current tab
	instance.tabs.currentWidget().register_address("github.com")
	if instance.tabs.currentWidget().current_url in instance.bookmark_list:
		assert True
	else:
		assert False

######### Tests for Zoom In and Zoom Out Features #########
# Method to test that the font size increases when zoom_in is called
def test_zoom_in():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("google.com")
	starting_font_size = instance.tabs.currentWidget().font_size
	starting_title_font_size = instance.tabs.currentWidget().title_font_size

	instance.tabs.currentWidget().zoom_in()

	# Text should be larger than when it first started out
	if starting_font_size < instance.tabs.currentWidget().font_size and starting_title_font_size < instance.tabs.currentWidget().title_font_size:
		assert True
	else:
		assert False

# Method to test that the font size changes when zoom_in is called
def test_zoom_out():
	app = QApplication(sys.argv)
	instance = web_gui.BrowserWindow(None)
	instance.tabs.currentWidget().register_address("google.com")
	starting_font_size = instance.tabs.currentWidget().font_size
	starting_title_font_size = instance.tabs.currentWidget().title_font_size

	instance.tabs.currentWidget().zoom_out()

	# Text should be smaller than when it first started out
	if starting_font_size > instance.tabs.currentWidget().font_size and starting_title_font_size > instance.tabs.currentWidget().title_font_size:
		assert True
	else:
		assert False

'''
Methods to test how fast the browser can load different websites. They always assert true
but they print out the amount of time (in seconds) it takes to load the webpage
(NOTE: only prints results if file is run directly (e.g. "python test.py"))
(NOTE: doesn't detect whether website was actually sucessfully loaded)
NOTE: Currently doesn't work unless the contents of update_tab_title_outside are commented out
'''
def test_google_time():
	f = open("performanceMetrics.txt", "w+")
	start_time = time.time()

	app = QApplication(sys.argv)
	a_window = web_gui.BrowserWindow(None)
	a_window.add_tab()
	a_window.tabs.currentWidget().register_address('google.com')

	f.write("Time to load 'google.com' in seconds: " + str(time.time()-start_time)+ "\n")
	assert True

def test_youtube_time():
	f = open("performanceMetrics.txt", "a+")
	start_time = time.time()

	app = QApplication(sys.argv)
	a_window = web_gui.BrowserWindow(None)
	a_window.add_tab()

	a_window.tabs.currentWidget().register_address('youtube.com')
	f.write("Time to load 'youtube.com' in seconds: " + str(time.time()-start_time)+ "\n")
	assert True

def test_upedu_time():
	f = open("performanceMetrics.txt", "a+")
	start_time = time.time()

	app = QApplication(sys.argv)
	a_window = web_gui.BrowserWindow(None)
	a_window.add_tab()

	a_window.tabs.currentWidget().register_address('up.edu')
	f.write("Time to load 'up.edu' in seconds: " + str(time.time()-start_time) + "\n")
	assert True

def test_amazon_time():
	f = open("performanceMetrics.txt", "a+")
	start_time = time.time()

	app = QApplication(sys.argv)
	a_window = web_gui.BrowserWindow(None)
	a_window.add_tab()

	a_window.tabs.currentWidget().register_address('amazon.com')
	f.write("Time to load 'amazon.com' in seconds: " + str(time.time()-start_time)+ "\n")
	assert True

def test_wiki_time():
	f = open("performanceMetrics.txt", "a+")
	start_time = time.time()

	app = QApplication(sys.argv)
	a_window = web_gui.BrowserWindow(None)
	a_window.add_tab()

	a_window.tabs.currentWidget().register_address('en.wikipedia.org/wiki/Main_Page')
	f.write("Time to load 'en.wikipedia.org/wiki/Main_Page' in seconds: " + str(time.time()-start_time) + "\n")
	assert True

'''
Method to test web_parse.py
'''
def test_replace_code():
	inst = web_parse.Parse()
	input_string = "Th&#169;i&#39;s s&#038;ent&#8217;enc&quot;e is &copy;whole ag&#8211;ain.&amp;"
	output_string = inst.replace_code(input_string)
	assert output_string == "Th(c)i\'s s&ent\'enc\"e is (c)whole ag-ain.&"

# def test_tag_list():
# 	try:
# 		doc_1 = open("../HTML_for_Pytest.html", "r")
# 		doc_2 = open("../HTML_file1.html", "r")
# 		parse_instance_1 = web_parse.Parse()
# 		parse_instance_1.get_data_to_parse(doc_1.read())
# 		parse_instance_2 = web_parse.Parse()
# 		parse_instance_2.get_data_to_parse(doc_2.read())
# 		assert True
# 	except IOError:

# 		assert False

# def test_web_parse_hyperlinks():
# 		badLink = '"<a href="htttp://example.com">"'
# 		parse_instance_1 = web_parse.Parse()
# 		data = parse_instance_1.get_data_to_parse(badLink)
# 		if(data == None): assert False

# 		assert True

if __name__ == "__main__":
	test_google_time()
	test_upedu_time()
	test_youtube_time()
	test_amazon_time()
	test_wiki_time()
	attempt_to_bookmark_same_url()
