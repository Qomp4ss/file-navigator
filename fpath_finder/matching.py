from pathlib import Path
import re

def eq(string, pattern):
      return string == pattern
          
def isin(string, pattern):
     return pattern in string
          
def regex(string, pattern):
      return True if re.search(pattern, string) else False

def glob(string, pattern):
      return Path(string).match(pattern)
