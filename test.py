'''
NOTE: The majority of our test cases are located in ./Browser/test.py
'''

#!/usr/bin/python
import parser

# Check if we can sucessfully open and read a given file
def test_parser_videos():
	try:
		doc = open("HTML_file1.html", "r")
		doc.close()
		assert True
	except IOError:
		assert False
