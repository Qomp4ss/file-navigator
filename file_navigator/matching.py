from pathlib import Path
import re

def eq(string, pattern):
    """
    Equality matching function.
    
    Parameters
    ----------
    string: str
        String with which pattern will be compared.
    pattern: str
        String pattern to be match.
    
    Retruns
    -------
    bool
        True/False if string and a pattern are equal.
    """
    return string == pattern
          
def isin(string, pattern):
    """
    Inclusion matching function.
    
    Parameters
    ----------
    string: str
        String in which pattern will be searched.
    pattern: str
        String pattern to be searched.
    
    Retruns
    -------
    bool
        True/False if pattern is in the string.
    """
    return pattern in string
          
def regex(string, pattern):
    """
    Regex matching function supporting standard strings and file-paths/
    
    Parameters
    ----------
    string: str
        String in which regex pattern will serached.
    pattern: str
        String regex pattern to be searched.
    
    Retruns
    -------
    bool
        True/False if regex pattern was found in the string.
    """
    return True if re.search(pattern, string) else False

def glob(string, pattern):
    """
    Glob matching function supporting standard strings and file-paths.
    
    Parameters
    ----------
    string: str
        String in which glob pattern will serached.
    pattern: str
        String glob pattern to be searched.
    
    Retruns
    -------
    bool
        True/False if glob pattern was found in the string.
    """
    return Path(string).match(pattern)
