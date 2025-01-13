"""
Abstract & Concrete Loader classes
"""
from abc import ABC, abstractmethod
import inspect
from pathlib import Path
from functools import lru_cache

class ABLoader(ABC):
    """
    Loader Abstract Base Class
    
    Interface which all Loader objects must implement, to ensure that 
    dependency injection in _PathManager.load method will work as expected.
    """
    @abstractmethod
    def load(self, path, **kwargs):
        """
        Abstract function for loading data using file path.
        
        Parameters
        ----------
        path: path-like object.
        kwargs: dict
        """
        raise NotImplementedError("This has to be implemented")

class BaseLoader(ABLoader):
    """
    Simple Loader Factory
    
    Class that implements ABLoader interface allowing to dynamically create loader objects, 
    based on a dictionary with loading functions and extension_type(s) pairs.
    
    Parameters:
        func_ftype_dict (Dict[callable : str | list][default=None]): Dictionary 
            with loading functions and extension_type(s) pairs.
    
    Attributes:
        _mapp (dict): Empty dict to which loading functions and extension_type(s)
            pairs will be added.
    
    Methods:
        add_functions (func_ftype_dict: Dict[callable : str | list]]): Function
            to add at least one loading function and extension_type(s) entry.
        load (path: str, kwargs: dict): Function for loading data specified by 
            a file path, distributing matching key-value arguments to all of the 
            available loader functions.            
    """
    def __init__(self, func_ftype_dict = None):
        self._mapp = {}
        if func_ftype_dict is not None:
            self.add_functions(func_ftype_dict)

    def _add(self, func, file_type):
        """
        Private function for adding single mapping of loader function and file type.
        
        Function that adds and validates a single entry of a loader function 
        and file type mapping.
        
        Parameters
        ----------
        func: Callable
            Loading function.
        file_type: str | list
            String or list of strings representing file types (extensions).
        
        Returns
        -------
        None
        """
        if not callable(func):
            raise TypeError(f"{func} is not callable")

        if not isinstance(file_type, (str, list)):
            raise TypeError(f"{file_type} must be passed as either string or list")

        if isinstance(file_type, list):
            for f_t in set(file_type):
                if not isinstance(f_t, str):
                    raise TypeError(f"{f_t} must be passed as a string")
                self._mapp[f_t] = func
        else:
            self._mapp[file_type] = func

    def add_functions(self, func_ftype_dict):
        """
        Function for adding multiple loader function and file type mappings.
        
        Function that allows adding multiple loader function and file type 
        mappings, by iteratively calling _add method.
        
        Parameters
        ----------
        func_ftype_dict: Dict[callable : str | list]
            Dictionary with loading functions and extension_type(s) pairs.
        
        Returns
        -------
        None
        """
        if not isinstance(func_ftype_dict, dict):
            raise TypeError('func_ftype_dict must be of dictionary type')
        for k, v in func_ftype_dict.items():
            self._add(k, v)

    def _inspect(self, function):
        """
        Private function for returning all of the parameters accepted by a loader function.
        
        Parameters
        ----------
        function: Callable
            Function whose parameters have to be retrieved.
        
        Returns
        -------
        odict_keys
            Collection of the parameters accepted by the function.
        """
        return inspect.signature(function).parameters.keys()

    @lru_cache(maxsize=128)
    def load(self, path, **kwargs):
        """
        Implementation of ABLoader interface.
        
        Function implementing ABLoader interface, delegating loading data 
        operations to a loader function based on the pre-defined file type,
        from a file specified by a path-like string, distributing matching key-value 
        arguments to all of the available loader functions.
        
        Parameters
        ----------
        path: str
            Path-like string pointing to an existing file.
        kwargs: dict
            Key, value arguments to be distributed to loader functions.
        
        Returns
        -------
        obj
            Object loaded by the delegate function.
        """
        func = self._mapp[Path(path).suffix]
        return func(path, **{k:v for k, v in kwargs.items() if k in self._inspect(func)})
    