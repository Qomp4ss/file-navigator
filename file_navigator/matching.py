"""
Module with matching functions
"""
import re
from pathlib import Path

def eq(string, pattern):
    """
    Equality matching function.
    
    Parameters
    ----------
    string: str
        String with which pattern will be compared.
    pattern: str
        String pattern to be matched.
    
    Returns
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
    
    Returns
    -------
    bool
        True/False if pattern is in the string.
    """
    return pattern in string

def regex(string, pattern):
    """
    Regex matching function supporting standard strings and file paths.
    
    Parameters
    ----------
    string: str
        String in which regex pattern will be searched.
    pattern: str
        String regex pattern to be searched.
    
    Returns
    -------
    bool
        True/False if regex pattern was found in the string.
    """
    return bool(re.search(pattern, string))

def glob(string, pattern):
    """
    Glob matching function supporting standard strings and file paths.
    
    Parameters
    ----------
    string: str
        String in which glob pattern will be searched.
    pattern: str
        String glob pattern to be searched.
    
    Returns
    -------
    bool
        True/False if glob pattern was found in the string.
    """
    return Path(string).match(pattern)
