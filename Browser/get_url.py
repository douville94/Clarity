# -*- coding: utf-8 -*-
# To access web pages from the web
import re
# regular expressions for parsing html
import re
# To provide access to low-level
import socket

# Manages high-level HTTP requests
import requests

# Import method to parse html of a given url
import web_parse


# Takes in an url and gets its data
def parse_site(url):
#    print("\n")
#    print("---------------------")
#    print("r.text: ", requests.get(url, auth=requests.auth.HTTPBasicAuth("user", "pass")).text)
#    print("---------------------")
#    print("\n")
    try:
        headers = {}
        headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36  "
#        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/51.0"

#        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/51.0"
        #Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0)

        #Send out DNS query (lines taken from:  https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts )
#         if "http://" in url:
#             noPrefixUrl = url.lstrip("http://")
#         elif "https://" in url:
#             noPrefixUrl = url.lstrip("https://")
#         print(socket.gethostbyname("localhost")) # result from hosts file
#         ipAddress = socket.gethostbyname(noPrefixUrl) # your OS sends out a DNS query
# #        ipAddress = socket.getaddrinfo("www.up.edu", "https")
#         print("Entered Website: ", url)
#         print("TCP/IP address of entered Website: ", ipAddress)

        # If the passed in 'url' doesn't have an implicit 'http://' at the beginning, we can assume it needs one
        # and append it to the url string.
        dummyHttp = 'https://'
        checkUrl = re.findall('^https?://', url)
        if not checkUrl:
            url = dummyHttp + url
#        headers = { #for whatever reason when the UA string is formatted this way, we can connect to amazon.
#            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
#        }


        headers = { #for whatever reason when the UA string is formatted this way, we can connect to amazon.
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        }


        #Use the high-level requests package
#        r = requests.get(url, headers = headers )
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth("user", "pass"))
        r = requests.get(url, headers = headers )
        print("Status code: ", r.status_code)
        resp = r.text
        saveFile = open("websiteOutput.txt", "w")
#        saveFile.write(str(resp))
        saveFile.write(resp)
        saveFile.close()

#        print("\n")
#        print(str(resp))
#        print("\n")

        parse_instance = web_parse.Parse()
        parse_instance.original_url = url

        # Return the HTML code that we want to parse
        return parse_instance.get_data_to_parse(r.text)

    # If unable to open site, print the resulting error
    except Exception as e:
        print("Exception in get_url!")
        print("Reason: " + str(e))
#        return re.findall(r"<p>(.*?)</p>", str(respData))


    # output = {}
    # Regular Expressions for parsing HTML tags
    # Paragraphs: (<p> Some text </p>)
#    return re.findall(r"<p>(.*?)</p>", str(respData))

    # return ["output", "hello"]

if __name__ == "__main__":
    print(parse_site("http://pythonprogramming.net"))
