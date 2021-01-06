'''
Creates an instance to parse through website data (HTML, CSS, & JavaScript).
Can be called through get_url to parse through website data or it can be run on
a file by running this file directly (see bottom of file)
'''
import re
#tinycss is a simple CSS parser for Python.  Install via "pip install tinycss" through command line
#import tinycss
import sys
import os
import requests
#import tinycss
#import web_gui

#Variable values:
#text = a particular portion of HTML code with whitespace excised
#rawText = all HTML code with whitespace excised
#partialLink = match object returned after searching all html code for href (an HTML attribute specifying a Webpage's URL), whitespace, any chars, ', "
#path: a particular URL parsed from HTML href attribute

class Parse():
    def __init__(self):
        super().__init__()
        self.original_url = ""
        self.data_to_parse = "" # String to hold data to parse through
        self.open_tags = []
        self.close_tags = []
        self.video_links = []
        self.image_links = []
        self.results = []

    # Obtains the text (html, css, and JavaScript) to parse through
    def get_data_to_parse(self, received_data):
        #Command-line shell output:  "maximum recursion depth exceeded"
        #Increase recursion depth
        #Source:  https://stackoverflow.com/questions/3323001/what-is-the-maximum-recursion-depth-in-python-and-how-to-increase-it
        sys.setrecursionlimit(50000)

        # removes all the java script from the html data.
        received_data = self.remove_script(received_data)

        self.data = received_data # updates the data to be parsed through
        self.tags_list(0) # Parse from the beginning to find readable html
        # this is needed for appending the original url to partial links
        # Prints out only the visual elements of the html document
        # Puts the data into tuples: (type, text)
        for num in range(0, len(self.open_tags)-1):

            # If the tag is a title then print out the text inside the tag.
            if self.data.startswith( 'title', self.open_tags[num]+1, self.close_tags[num] ):
                title = self.data[self.close_tags[num]+1:self.open_tags[num+1]]
                title = self.replace_code(title)
                if title is not "" and title is not None:
                    self.results.append(('title', title))
            # Prints header section.
            elif self.data.startswith( 'h', self.open_tags[num]+1, self.close_tags[num] ):
                title = self.data[self.close_tags[num]+1:self.open_tags[num+1]].strip()
                title = self.replace_code(title)
                if title is not "" and title is not None:
                    self.results.append(('h', title))
            # Prints paragraph section.
            elif self.data.startswith( 'p', self.open_tags[num]+1, self.close_tags[num] ):
                title = self.data[self.close_tags[num]+1:self.open_tags[num+1]].strip()
                title = self.replace_code(title)
                if title is not "" and title is not None:
                    self.results.append(('p', title))
            elif self.data.startswith('style', self.open_tags[num] + 1, self.close_tags[num]):
                text = self.data[self.close_tags[num] + 1:self.open_tags[num + 1]].strip()
                if text is not "" and text is not None:
                    self.results.append(('css', text))
            # CSS
#            elif self.data.startswith('link href', self.open_tags[num] + 1, self.close_tags[num]):
#            elif self.data.endswith('.css', self.open_tags[num] + 1, self.close_tags[num]):
#                link = None
#                rawText = self.data[self.open_tags[num] + 1 : self.close_tags[num]].strip()
#                partialLink = re.search(r'(href=\s?[\'\"])(.+?)([\'\"])', rawText) #link in group(2)
#                if partialLink:
#                    if not partialLink.group(2).startswith("__"):
#                        link = partialLink.group(2)
#                if link:
#                    if re.match(r'//', link):
#                        link = "https:" + link
#                    elif re.match(r'/', link):
#                        if self.original_url.endswith('/'):
#                            link = self.original_url + link[1:]
#                        else:
#                            link = self.original_url + link
#                partialLinkStr = str(partialLink)
#                partialLinkStr = partialLinkStr.strip("<>")
#                linkStr = str(link)
#                linkStr = linkStr.strip("<>")
#                text = requests.get(partialLinkStr, auth=requests.auth.HTTPBasicAuth("user", "pass")).text
#                self.results.append(('css', text))

            # Prints attribute section.
            elif self.data.startswith( 'a', self.open_tags[num]+1, self.close_tags[num] ):
                rawText = self.data[self.open_tags[num] + 1 : self.close_tags[num]].strip()
                #using regex to grab the hyperlink from the <a....> tag
                #grabFormatChars = re.findall('[\\n\\t]+', rawText)  # findall non printable ascii chars

                #link = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', rawText)

                # determine what the title should be.
                titleMatch = re.search(r'(\stitle=\s?[\'\"])(.+?)([\'\"])', rawText) #title in group(2)
                #REGEX SYNTAX BREAKDOWN:
                #re: Python regex package
                #re.search(): search function that returns a boolean match object
                #r: placed before a string literal to allow backslashes to be read as chars i.e. prevent special handling of backslashes IN PYTHON
                #\: escapes a special char
                #\s: whitespace
                #?: quantifier indicating the previous char literal occurs once or none in the searched text
                #+: quantifier indicating the previous char literal occurs once or more in the searched text
                #.: any char except line break
                #\': '
                #\": "
                #(: specifies capturing group
                #): close specification of capture group
                #[: chars in the brackets specified are subject to operation(s) specified before the brackets
                #]: close specified chars to be operated on
                title = None
                if titleMatch:
                    title = titleMatch.group(2)
                elif not (self.data[self.close_tags[num] + 1:self.open_tags[num + 1]].strip() is ""):
                    title = self.data[self.close_tags[num] + 1:self.open_tags[num + 1]]

                # determine what the hyperlink url is.
                partialLink = re.search(r'(href=\s?[\'\"])(.+?)([\'\"])', rawText) #link in group(2)
                link = None
                if partialLink:
                    if not partialLink.group(2).startswith("__"):
                        link = partialLink.group(2)
                if link:
                    if re.match(r'//', link):
                        link = "https:" + link
                    elif re.match(r'/', link):
                        if self.original_url.endswith('/'):
                            link = self.original_url + link[1:]
                        else:
                            link = self.original_url + link

                # if we have all the information then add to our results!
                if link is not None and title is not None:
                    self.results.append(('a', (str(self.replace_code(title)), str(link))))
                #elif link is None:
                    #print ("\nThe text", rawText, "did not contain a link.")
                #elif title is None:
                    #print("\nThe text", rawText, "did not contain a title.")
                #checkPartialLink = str(partialLink).find('//') #I needed to do this for formatting sake. Now hyperlinks won't show up twice.

                #if link:
                    #self.results.append(('a', (self.data[self.close_tags[num] + 1:self.open_tags[num + 1]], link[0])))

                #if partialLink:
                    #if checkPartialLink is -1:
                        #self.results.append(('a', (self.data[self.close_tags[num] + 1:self.open_tags[num + 1]], self.original_url + partialLink[0])))
            # Prints table text.
            elif self.data.startswith( 'th', self.open_tags[num]+1, self.close_tags[num] ):
                text = self.data[self.close_tags[num]+1:self.open_tags[num+1]].strip()
                text = self.replace_code(text)
                self.results.append(('th', text))
            # Placeholder for video links
            elif self.data.startswith('video', self.open_tags[num]+1, self.close_tags[num]):
                self.results.append(('video',"Found a video! \n" ))
                self.video_links.append(self.data[self.close_tags[num]+1:self.open_tags[num+1]])
            # Placeholder for image links
            elif self.data.startswith('img', self.open_tags[num]+1, self.close_tags[num]):
                path = self.find_path(self.data[self.open_tags[num]:self.close_tags[num]])
                text = self.find_alt(self.data[self.open_tags[num]:self.close_tags[num]])
                # store the source path and the text in the results if the path exists.
                if text is "" or text is None:
                    text = "Untitled Image"
                if path is not None:
                    self.results.append(('img',(str(path), str(self.replace_code(text)))))
                #self.image_links.append(self.data[self.close_tags[num]+1:self.open_tags[num+1]])
            # Prints CSS
            elif self.data.startswith('link href=', self.open_tags[num] + 1, self.close_tags[num]):
                path = self.find_path(self.data[self.open_tags[num]:self.close_tags[num]])
                print("\n----------------------------------\npath: ", path)#This doesn't work for some reason
                
                # determine what the hyperlink url is.
                rawText = self.data[self.open_tags[num] + 1 : self.close_tags[num]].strip()
                partialLink = re.search(r'(href=\s?[\'\"])(.+?)([\'\"])', rawText) #link in group(2)
                link = None
                if partialLink:
                    if not partialLink.group(2).startswith("__"):
                        link = partialLink.group(2)
#                        text = requests.get(link, auth = requests.auth.HTTPBasicAuth("user", "pass")).text
#                        textStr = str(text)
                if link:
                    if re.match(r'//', link):
#                        link = "https:" + link
                        newLink = "http:"
                        newLink += link
                        text = requests.get(newLink, auth = requests.auth.HTTPBasicAuth("user", "pass")).text
                        textStr = str(text)
                    elif re.match(r'/', link):
                        if self.original_url.endswith('/'):
                            link = self.original_url + link[1:]
                            text = requests.get(newLink, auth = requests.auth.HTTPBasicAuth("user", "pass")).text
                            textStr = str(text)
                        else:
                            link = self.original_url + link
                            text = requests.get(link, auth = requests.auth.HTTPBasicAuth("user", "pass")).text
                            textStr = str(text)
                print("\n----------------------------------\nlink: ", link)
                print("\n----------------------------------\npartialLink: ", partialLink)
#                if not link.startswith("http://"):
#                    newLink = "http://"
#                    newLink += link
                #get file from path
                text = requests.get(path, auth=requests.auth.HTTPBasicAuth("user", "pass"))#.text
#                text = requests.get(newLink, auth = requests.auth.HTTPBasicAuth("user", "pass")).text
                textStr = str(text)
                textStr = textStr.strip("<>")
                print("\n----------------------------------\n", textStr)
                self.results.append(('css', textStr))
            elif self.data.startswith('style', self.open_tags[num] + 1, self.close_tags[num]):
                text = self.data[self.close_tags[num] + 1:self.open_tags[num + 1]].strip()
                text = self.replace_code(text)
                self.results.append(('css', text))

        # print ("Web_parse: " + str(self.results))

        file = open("CSSOutput.txt", "w")
        self.getCSS(self.data, file, self.results, 0, len(self.data) - 1)
        file.close()
#        file = open("CSSOutput.txt", "w")
        # self.getCSS(self.data, file, 0, len(self.data) - 1)
#        file.close()
        #Reopen the CSS output file in read mode
#        file = open("CSSOutput.txt", "r")
        #Parse the CSS output
        #But first create BrowserWindow instance to pass into the function
#        browsInst = BrowserWindow()
#        browsInst = web_gui.BrowserWindow()
#        self.parseCSS(self.data, file, self.results, 0, len(self.data) - 1)#, browsInst)
#        p = tinycss.make_parser(

        #Incorporate CSS into self.results
        return self.results


    # replace certain characters.
    def replace_code(self, text):
        text = str(text)
        text = text.replace(r'&#8217;', '\'')
        text = text.replace('&#39;', '\'')
        text = text.replace('&#169;', '(c)')
        text = text.replace('&copy;', '(c)')
        text = text.replace('&quot;', '\"')
        text = text.replace('&amp;', '&')
        text = text.replace('&#038;', '&')
        text = text.replace('&#8211;', '-')
        return text

    # find the path src within the given text.
    def find_path(self, text):

#        # where does the path start.
#        path_s = text.find('src=')
#        if path_s == -1:
#            return None
#        else:
#            path_s = path_s + 4 # so that we don't include "src=" in the path
        # match the source path
        path = re.search(r'(?<=\ssrc=)\s*?[\'\"]([^\s\'\"]+)[\"\']', text)#(?=\s)

        # where does the path end.
#        path_e = text.find('=', path_s+4)
#        if path_e == -1:
#            path_e = len(text)
#        else:
#            path_e = text.rfind(" ", path_s, path_e) # this will be the space at the end of block we want.

        f = open("path.txt", "w")
        if path is not None:
            f.write(path)
            f.close()
        # if no match is found
        if path == None:
            print("MATCH: match not found from", text, "\n")
            f.write("MATCH: match not found from")
            f.write(text)
            f.write("\n")
            f.close()
            return None

        # return what is the path without quotes around it and without whitespace.
#        return text[path_s:path_e].strip().replace("\"","")
        return path.group(1)

    def find_alt(self, text):
        alt = re.search(r'(?<=alt=)\s*[\'\"]?([^\s\'\"]+)[\"\']?(?=\s)', text)
        #cue_start = self.data.find(cue)
        #text_s = self.data.find('\"', cue_start)
        #text_e = self.data.find('\"', text_s+1)
        if alt == None:
            return None

        return alt.group(1) #self.data[text_s+1:text_e]

    #remove the java script data from the passed in string.
    def remove_script(self, text):
        new_text = re.subn(r'<script.*?>[\s\S]*?</script>', "", text)
        # subn returns a tuple with entries (the new string, number of substitutions)
        return new_text[0]


    def tags_list(self, start):
        if start >= len(self.data):
            return
        open_tag_index = self.data.find("<", start)
        close_tag_index = self.data.find(">", start)
        # If an open or close tag exists...
        if open_tag_index != -1:
            # store the found indexes into the appropriate lists
            self.open_tags.append(open_tag_index)
            self.close_tags.append(close_tag_index)
            return self.tags_list(close_tag_index + 1) # Recursive call

    def getCSS(self, d, file, results, x, y):
        print("You're at the beginning of getCSS.\n")
        print("Current URL: ", self.original_url)
        print("\n")
        print("x = ", x)
        print("y = ", y)
        print("\n")
        tempString = ""#Initialize tempString
#        s = str(data)#Capture self.data as a string
        secondString = ""
        thirdString = ""
        endStyleTag = 0
        endDotCSS = 0
        for i in range(x, y + 1):#len(self.data) - 1):
            #Copy contents of HTML file in specified range into tempString
            tempString += d[i]#From:  https://stackoverflow.com/questions/4435169/how-do-i-append-one-string-to-another-in-python
            if d[i] == "/" and d[i + 1] == ">":
                print("Now at closing tag!")
                print("i = ", i)
                for l in range(i, y + 1):
                    thirdString += d[l]
                print("\n\nthirdString.find(\"/>\") = ", thirdString.find("/>"))
                print("\n")
                y = i + 1
                print("\n---------------------------------")
                print("y = ", y)
                print("len(d) - 1 = ", len(d) - 1)
                print("thirdString.find(\"/>\") = ", thirdString.find("/>"))
                print("d[y - 2] = ", d[y - 2])
                print("d[y - 1] = ", d[y - 1])
                print("d[y] = ", d[y])
                print("\n")
                if ".css" in tempString:
                    print("---------------------------------")
                    print("Index of .css in tempString = ", tempString.find(".css"))
                    print("Index of .css in d = ", d.find(".css", y, len(d)))
                    endDotCSS = d.find(".css", y - 5, len(d))
                    print("---------------------------------\n")
                    break
                break
            elif d[i] == "<" and d[i + 1] == "/":# and d[i + 6] == ">":#tempString goes from the beginning of a tag to the end of a tag
                print("Now at closing tag!")
                print("i = ", i)
                print("\nd.find(\">\") = ", d.find(">"))
                print("\n")
                for k in range(i, y + 1):
                    secondString += d[k]
                print("secondString.find(\">\") = ", secondString.find(">"))
                print("\n")
                for j in range(i + 1, i + secondString.find(">") + 1):
                    tempString += d[j]
#                    print("d[j] = ", d[j])
#                    print("\n")
                    if j == i + secondString.find(">"):
                        y = j
                        print("\n---------------------------------")
                        print("j = ", j)
                        print("y = ", y)
                        print("len(d) - 1 = ", len(d) - 1)
#                        print("tempString[j] = ", tempString[j])
                        print("secondString.find(\">\") + i = ", secondString.find(">") + i)
                        print("d[y - 2] = ", d[y - 2])
                        print("d[y - 1] = ", d[y - 1])
                        print("d[y] = ", d[y])
                        print("\n")
#                        print("tempString[y - 2] = ", tempString[y - 2])
#                        print("tempString[y - 1] = ", tempString[y - 1])
#                        print("tempString[y] = ", tempString[y])
                        if "</style>" in tempString:
                            print("---------------------------------")
                            print("Index of </style> in tempString = ", tempString.find("</style>"))
                            print("Index of </style> in d = ", d.find("</style>", j, len(d)))
                            endStyleTag = d.find("</style>", j, len(d))
                            print("---------------------------------")
                            print("\n")
                            break
                break

        print("\n--------------------------------")
        print("y after assignment = ", y)
        print("len(d) - 1 = ", len(d) - 1)
        print("--------------------------------\n")
        print("\n---------------------------------------------------")
        print("tempString = ", tempString)
        print("---------------------------------------------------\n")

        #CSS can appear in one of three ways: filename in HTML, label tag in HTML, or <style> tag in HTML

        #For embedded CSS
        if "<style>" in tempString:#Search tempString for "style" tag
            print("\n")
            a = d.find("<style>", x, endStyleTag + 1)#len(d) - 1)
#            a = tempString.find("<style>")
            print("---------------------------------------")
            print("<style> in tempString")
            print("a = ", a)
            b = d.find("</style>", a, endStyleTag + 8)#len(tempString) - 1)
#            b = tempString.find("</style>")
            print("b = ", b)
            print("\n")
            if a != -1 and b != -1:
                print("You're in the if statement!")
                for j in range(a, b + 8):
#                    print("You're in the for loop!")
                    file.write(d[j])
#                    file.write(tempString[j])
#                    results.append(d[j])#add the CSS to self.results
                    results.append(tempString)
                    if d[j] == ";" or d[j + 1] == "{" or d[j + 1] == "}" or d[j] == "{" or d[j] == "}":
#                    if tempString[j] == ";" or tempString[j + 1] == "{" or tempString[j + 1] == "}" or tempString[j] == "{" or tempString[j] == "}":
                        file.write("\n")
                        file.write("\t")
                #Increment indices one beyond </style> (closing style tag)
                b += 8
                a = b
                b += 1
                if b <= len(d) - 1 and a <= len(d) - 1:# and a != -1 and b != -1:#Check if at end of HTML file
                    self.getCSS(d, file, results, a, len(d) - 1)#Recursive call
                else:
#                    return file
                    return results
            else:
                print("\n------------------------------")
                print("Tag not found.")
                print("------------------------------\n")
                if x > len(d) - 1 or y > len(d) - 1:
#                    return file
                    return results
                else:
                    x = y
                    x += 8
                    y = x + 1
                    self.getCSS(d, file, results, x, len(d) - 1)
        #For separate CSS files
        elif ".css" in tempString:#Search tempString for links to actual CSS files
            a = d.find("<link href=", x, endDotCSS + 1)#y)#len(d) - 1)
            print("-----------------------")
            print(".css in tempString")
            print("a = ", a)
            b = d.find(".css", a, endDotCSS + 4)#y)#len(d) - 1)
            print("b = ", b)
            print("\n")
            CSSFilename = ""
            if a != -1 and b != -1:#Check that indices have been found
                if ".com" in tempString:#Search tempString for CSS file with an actual URL (UP's main Website has this)
                    CSSFilename += "http:"#//"
                    for j in range(a + 12, b + 4):
    #                    if self.d[j] != "/" and self.d[j + 1] != "/":#Don't have two slashes in a row
                        CSSFilename += d[j]
                    print("\n--------------------------------")
                    print("CSSFilename: ", CSSFilename)
                    print("\n--------------------------------\n")
                    r = requests.get(CSSFilename, auth=requests.auth.HTTPBasicAuth("user", "pass"))
                    file.write("\n\n---------------------------------\n")
                    file.write("CSS filename: " + CSSFilename)
                    file.write("\n---------------------------------\n")
                    file.write(r.text)
                    results.append(r.text)#Add the CSS to self.results
                    #Go to the next tag in the file
                    for i in range(b, len(d)):
                        if i <= len(d) - 1 and d[i] == ">":#"\n":
                            b += 4
                            a = b
                            b += 1
                            break
                    if b <= len(d) - 1 and a <= len(d) - 1 and b != -1 and a != -1:
                        self.getCSS(d, file, results, a, len(d) - 1)#Recursive call
                    else:
#                        return file
                        return results
                else:
                    a = d.find("<link href=", x, y)#len(self.d) - 1)
                    b = d.find(".css", a, y)#len(self.d) - 1)
                    CSSFilename = ""#empty CSSFilename
                    CSSFilename += self.original_url
                    CSSFilename += "/"
                    for j in range(a + 12, b + 4):
                        #if there's no newline character before ".css"
                        if d[j] != "\n":# and self.d[j] != "/":
                            CSSFilename += d[j]#from:  https://stackoverflow.com/questions/4435169/how-do-i-append-one-string-to-another-in-python
                    r = requests.get(CSSFilename, auth=requests.auth.HTTPBasicAuth("user", "pass"))
                    file.write("\n\n-----------------------------------\n")
                    file.write("CSS filename: " + CSSFilename)
                    file.write("\n-----------------------------------\n")
                    file.write(r.text)
#                    self.results.append(r.text)#Add the CSS to self.results
        #            for k in range(0, len(r.text)):
        #                file.write(CSSFile[k])
        #                if CSSFile[k] == ";" or CSSFile[k + 1] == "{" or CSSFile[k + 1] == "}" or CSSFile[k] == "{" or CSSFile[k] == "}":
        #                    file.write("\n")
        #                    file.write("\t")
                    #Go to the next line in the file
                    for i in range(b, len(d)):
                        if i <= len(d) - 1 and d[i] == ">":#"\n":
#                            a = b + i + 1
    #                        b = i + 1
                            b += 4
                            a = b
                            b += 1
                            break
                    if b <= len(d) - 1 and a <= len(d) - 1 and b != -1 and a != -1:
                        self.getCSS(d, file, results, a, len(d) - 1)#Recursive call
                    else:
#                        return file
                        return results
            else:
                print("\n------------------------------")
                print("Tag not found.")
                print("------------------------------\n")
                if x > len(d) - 1 or y > len(d) - 1:
#                    return file
                    return results
                else:
                    x = y
                    x += 5
                    y = x + 1
                    self.getCSS(d, file, results, x, len(d) - 1)
        #Move x and y to the next tag
        else:
            #If this is the last line in the HTML file
            if y >= len(d) - 1:# or y + 5 >= len(d) - 1:
                print("\nI couldn't find any CSS on this pass-through.\n")
                print("y = ", y)
                print("\n")
#                return file
                return results
            else:
                for i in range(y, len(d)):
                    #Move indices to next region to scan
                    if i + 1 <= len(d) - 1 and d[i] == ">":#"\n":
                        print("You're in the last else statement!\n")
                        print("i = ", i)
                        print("\n\nx = ", x)
                        print("\nlen(d) - 1 = ", len(d) - 1)
                        print("\n")
                        x = i + 1
                        break
                self.getCSS(d, file, results, x, len(d) - 1)#y)#Recursive call

    def parseCSS(self, d, f, r, x, y):#, browsInst):
        s = f.read()
        #From:  https://stackoverflow.com/questions/6181935/how-do-you-create-different-variable-names-while-in-a-loop
#        d = {}
#        for i in range(0, len(s)):
#            if s.find("CSSFilename: ", i) != -1:
#                #Store the CSS text as a new string
#                for j in range(i, len(s)):
#                    d["CSS{0}".format(i)] += s[j]
#                    if s.find("-------", i) != -1:
#                        break
        #For each CSS file stored as a string, parse the file
#        for k in range(0, len(d)):
#            if "," in d[k]:
#                pass

            #for l in d[k]:
                #if l == ",":
                    #pass
        tempString = ""
        w = 0
        for i in range(x, s.find("--------------") + 1):#y + 1):
            tempString += s[i]
            #don't use elifs so that every if statement gets executed
            if "width" in tempString:
                #capture the property
                index = tempString.find("width: ")
                a = index + 7
#                w = tempString[i + 7]
                #From:  https://stackoverflow.com/questions/4289331/python-extract-numbers-from-a-string
#                w = [int(tempString[index + 7]) for index + 7 in tempString.split() if tempString[index + 7].isdigit()]
#                print("\n------------------------------------------\n", [int(tempString[index + 7]) for index + 7 in tempString.split() if tempString[index + 7].isdigit()])
#                print("\n------------------------------------------\n")
#                for a in tempString.split():
#                for a in range(i + 7, len(tempString))
#                    if tempString[a].isdigit():
#                        w += int(tempString[a])
#                w = int("".join(filter(tempString.isdigit(), tempString)))
                print("\n---------------------------------------\n", w)
                continue
            if "height" in tempString:
                #capture the property
                index = tempString.find("height: ")
                a = index + 8
#                h = tempString[i + 8]
#                [int(tempString[index + 8]) for (index + 8) in tempString.split() if tempString[index + 8].isdigit()]
#                for a in tempString.split():
#                for a in range(index + 8, len(tempString)):
#                    if tempString[a].isdigit():
#                        w += int(tempString[a])
#                w = int("".join(filter(tempString.isdigit(), tempString)))
                print("\n-----------------------------------------\n", w)
                continue
            if "display" in tempString:
                #capture the property
                index = tempString.find("display: ")
                a = index + 9
#                disp = tempString[i + 9]
#                [str(tempString[index + 9]) for (index + 9) in tempString.split if re.search("AZ", tempString)]
#                for a in tempString.split():
#                    if tempString[a].isdigit():
#                        w = int(tempString[a])
#                w = int("".join(filter(tempString.isdigit(), tempString)))
                print("\n-----------------------------------------\n", w)
                continue
            if "flex" in tempString:#need to find out what "flex" is
                #capture the property
                continue
            if "solid" in tempString:#need to find out what "solid" is
                #capture the property
                continue
            else:
                if x == len(s) - 1 or y == len(s) - 1:
                    print("\nNo more CSS to parse.\n")
                    return
                for j in range(0, y + 1):
                    if s[j] == "---------------":
                        x += j
                self.parseCSS(d, f, r, x, y)

            #Render the captured properties
            #pass in values to web_gui.__init__()
#            browsInst.init_ui(width, height, etc)


        #Maybe do tag-by-tag regex instead?
        #Regex sucks
        #Do it anyway
        dict = {}
        n = 1
        for i in range(0, len(d)):
            if "link href=" in d:
                dict["CSSFile_{}".format(n)] = d[i]
                n += 1
        print("\n\n\n\ndict = ", dict)


    def give_original_url(self,url): #Need to retrieve the original url for hyperlink purposes.
        self.original_url = url

# Opens a file to parse through if web_parse.py is run directly
if __name__ == "__main__":
    try:
        doc = open("../HTML_for_Pytest.html", "r")
        parse_instance = Parse() # Create a parse instance
        parse_instance.get_data_to_parse(doc.read())
        doc.close()
    except IOError:
        print ("Unable to open the specified file.")
