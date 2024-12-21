from pathlib import Path
import fnmatch
import re

def eq(string, pattern):
      return string == pattern
          
def isin(string, pattern):
     return pattern in string
          
def regex(string, pattern):
      return re.match(pattern, string)

def glob(string, pattern):
      return Path(string).match(pattern)

def re_glob(string, pattern):
      return regex(string, fnmatch.translate(re.sub(r'\\(?=\|)', '', pattern)))