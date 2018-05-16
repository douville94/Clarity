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
            # Prints attribute section.
            elif self.data.startswith( 'a', self.open_tags[num]+1, self.close_tags[num] ):
                rawText = self.data[self.open_tags[num] + 1 : self.close_tags[num]].strip()
                #using regex to grab the hyperlink from the <a....> tag
                #grabFormatChars = re.findall('[\\n\\t]+', rawText)  # findall non printable ascii chars

                #link = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', rawText)

                # determine what the title should be.
                titleMatch = re.search(r'(\stitle=\s?[\'\"])(.+?)([\'\"])', rawText) #title in group(2)
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
        # print ("Web_parse: " + str(self.results))

        file = open("CSSOutput.txt", "w")
        # self.getCSS(self.data, file, 0, len(self.data) - 1)
        file.close()
        #Reopen the CSS output file in read mode
        file = open("CSSOutput.txt", "r")
        #Parse the CSS output
        self.parseCSS(file)
#        p = tinycss.make_parser(

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
        # if no match is found
        if path == None:
            print("MATCH: match not found from", text, "\n")
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

    def getCSS(self, d, file, x, y):
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
        i = x
        for i in range(x, y + 1):#len(self.data) - 1):
            #Copy contents of HTML file in specified range into tempString
            tempString += d[i]#From:  https://stackoverflow.com/questions/4435169/how-do-i-append-one-string-to-another-in-python
            if d[i] == "/" and d[i + 1] == ">":
                print("Now at closing tag!")
                print("i = ", i)
                print("\n")
                print("\n")
                for l in range(i, y + 1):
                    thirdString += d[l]
                print("thirdString.find(\"/>\") = ", thirdString.find("/>"))
                print("\n")
                y = i + 1
                print("\n")
                print("---------------------------------")
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
                    print("---------------------------------")
                    print("\n")
                    break
                break
            elif d[i] == "<" and d[i + 1] == "/":# and d[i + 6] == ">":#tempString goes from the beginning of a tag to the end of a tag
                print("Now at closing tag!")
                print("i = ", i)
                print("\n")
                print("d.find(\">\") = ", d.find(">"))
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
                        print("\n")
                        print("---------------------------------")
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

        print("\n")
        print("--------------------------------")
        print("y after assignment = ", y)
        print("len(d) - 1 = ", len(d) - 1)
        print("--------------------------------")
        print("\n")
        print("\n")
        print("---------------------------------------------------")
        print("tempString = ", tempString)
        print("---------------------------------------------------")
        print("\n")

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
                    if d[j] == ";" or d[j + 1] == "{" or d[j + 1] == "}" or d[j] == "{" or d[j] == "}":
#                    if tempString[j] == ";" or tempString[j + 1] == "{" or tempString[j + 1] == "}" or tempString[j] == "{" or tempString[j] == "}":
                        file.write("\n")
                        file.write("\t")
                #Increment indices one beyond </style> (closing style tag)
                b += 8
                a = b
                b += 1
                if b <= len(d) - 1 and a <= len(d) - 1:# and a != -1 and b != -1:#Check if at end of HTML file
                    self.getCSS(d, file, a, len(d) - 1)#Recursive call
                else:
                    return file
            else:
                print("\n")
                print("------------------------------")
                print("Tag not found.")
                print("------------------------------")
                print("\n")
                if x > len(d) - 1 or y > len(d) - 1:
                    return file
                else:
                    x = y
                    x += 8
                    y = x + 1
                    self.getCSS(d, file, x, len(d) - 1)
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
                    print("\n")
                    print("--------------------------------")
                    print("CSSFilename: ", CSSFilename)
                    print("\n")
                    print("--------------------------------")
                    print("\n")
                    r = requests.get(CSSFilename, auth=requests.auth.HTTPBasicAuth("user", "pass"))
                    file.write("\n")
                    file.write("\n")
                    file.write("---------------------------------")
                    file.write("\n")
                    file.write("CSS filename: " + CSSFilename)
                    file.write("\n")
                    file.write("---------------------------------")
                    file.write("\n")
                    file.write(r.text)
                    #Go to the next tag in the file
                    for i in range(b, len(d)):
                        if i <= len(d) - 1 and d[i] == ">":#"\n":
                            b += 4
                            a = b
                            b += 1
                            break
                    if b <= len(d) - 1 and a <= len(d) - 1 and b != -1 and a != -1:
                        self.getCSS(d, file, a, len(d) - 1)#Recursive call
                    else:
                        return file
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
                    file.write("\n")
                    file.write("\n")
                    file.write("-----------------------------------")
                    file.write("\n")
                    file.write("CSS filename: " + CSSFilename)
                    file.write("\n")
                    file.write("-----------------------------------")
                    file.write("\n")
                    file.write(r.text)
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
                        self.getCSS(d, file, a, len(d) - 1)#Recursive call
                    else:
                        return file
            else:
                print("\n")
                print("------------------------------")
                print("Tag not found.")
                print("------------------------------")
                print("\n")
                if x > len(d) - 1 or y > len(d) - 1:
                    return file
                else:
                    x = y
                    x += 5
                    y = x + 1
                    self.getCSS(d, file, x, len(d) - 1)
        #Move x and y to the next tag
        else:
            #If this is the last line in the HTML file
            if y >= len(d) - 1:# or y + 5 >= len(d) - 1:
                print("\n")
                print("I couldn't find any CSS on this pass-through.")
                print("\n")
                print("y = ", y)
                print("\n")
                return file
            else:
                for i in range(y, len(d)):
                    #Move indices to next region to scan
                    if i + 1 <= len(d) - 1 and d[i] == ">":#"\n":
                        print("You're in the last else statement!")
                        print("\n")
                        print("i = ", i)
                        print("\n")
                        print("\n")
                        print("x = ", x)
                        print("\n")
                        print("len(d) - 1 = ", len(d) - 1)
                        print("\n")
                        x = i + 1
                        break
                self.getCSS(d, file, x, len(d) - 1)#y)#Recursive call

    def parseCSS(self, f):
        s = f.read()
        #From:  https://stackoverflow.com/questions/6181935/how-do-you-create-different-variable-names-while-in-a-loop
        d = {}
        for i in range(0, len(s)):
            if s.find("CSSFilename: ", i) != -1:
                #Store the CSS text as a new string
                for j in range(i, len(s)):
                    d["CSS{0}".format(i)] += s[j]
                    if s.find("-------", i) != -1:
                        break
        #For each CSS file stored as a string, parse the file
        for k in range(0, len(d)):
            if "," in d[k]:
                pass

            #for l in d[k]:
                #if l == ",":
                    #pass

        #Maybe do line-by-line regex instead?

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
