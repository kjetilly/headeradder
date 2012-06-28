#!/usr/bin/env python
import re
import os
import argparse
import sys
import datetime
import codecs
def add_header_c(header, keyword):
    if keyword.find("%d") > -1:
        keyword = keyword % datetime.datetime.now().year
    text =  ""
    text += "/* %s\n" % keyword
    for i in range(len(header)):
        line = header[i]
        if i < len(header) - 1:
            text += " * %s" % line
        else:
            text += " * %s */" % line
    text += "\n\n"
    return text

# Note: this function will break in the year 10000
def has_header_c(text, keyword):
    keyword_year = keyword.find("%d")
    if keyword_year > -1:
        keyword_first = re.escape(keyword[:keyword_year])
        keyword_end = re.escape(keyword[keyword_year + 2: ])
        keyword = keyword_first + "\d{4}" + keyword_end
    else:
        keyword = re.escape(keyword)
    return re.match("^\s*\/\* %s" % keyword,text) != None

class Header:
    def __init__(self, header, keyword):
        self.header = header
        self.keyword = keyword
        
        # Handle different fileformats (most notably: html-style-comments vs. 
        # C-style-comments
        self.checks = {".cpp" : has_header_c,
                       ".c"   : has_header_c,
                       ".js"  : has_header_c,
                       ".h"   : has_header_c,
                       ".hpp" : has_header_c}
        self.writers = {".cpp" : add_header_c,
                        ".c"   : add_header_c,
                        ".js"  : add_header_c,
                        ".h"   : add_header_c,
                        ".hpp" : add_header_c}
    
    def add_header(self, filename):
        extension = os.path.splitext(filename)[1]
        if self.checks.get(extension) == None or self.writers.get(extension)==None:
            print("Could not find writer or checker for extension %s." % extension)
            print("Skipping file %s." % filename)
            return
        with codecs.open(filename, "r+", "utf8") as f:
            text = f.read()

            # Check if we should add header
            if not self.checks[extension](text, self.keyword):
                text = self.writers[extension](self.header, self.keyword) + text
                f.seek(0)
                f.write(text)
            else:
                print("Found header in %s" % filename)


def recurse(dirname, header):
    print ("Recursing into %s" % dirname)
    if os.path.isdir(dirname):
        print("Found a directory, looping through each file")
        for f in os.listdir(dirname):
            recurse(os.path.join(dirname, f), header)
    else:
        header.add_header(dirname)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename")
    parser.add_argument("-e", "--headerfile")
    parser.add_argument("-k", "--keyword")
    parser.add_argument("-r", "--recurse")
    args = parser.parse_args()
    header_file = args.headerfile
    filename = args.filename
    keyword = args.keyword
    recursedir = args.recurse

    header = []

    with open(header_file, "r") as header_lines:
        for line in header_lines:
            header.append(line)
    h = Header(header, keyword)
    if not recursedir == None:
        print("Recursing")
        recurse(recursedir, h)
    else:
        h.add_header(filename)
