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
        raise NotImplementedError("This have to be implemented")

class BaseLoader(ABLoader):
    """
    Simple Loader Factory
    
    Class that implents ABLoader interface allowing to dynamicly create loader objects, 
    based on a dictionary with loading functions and extension_type(s) paris.
    
    Parameters:
        func_ftype_dict (Dict[callable : str | list][default=None]): Dictionary 
            with loading functions and extension_type(s) paris.
    
    Attributes:
        _mapp (dict): Empty dict to which loading functions and extension_type(s)
            paris will be added.
    
    Methods:
        add_functions (func_ftype_dict: Dict[callable : str | list]]): Function
            to add at least one loading functions and extension_type(s) entry.
        load (path: str, kwargs: dict): Function for loading data sprecifed by 
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
            String or list of strings reperesenting file types (extentions).
        
        Retruns
        -------
        None
        """
        if not callable(func):
            raise TypeError(f"{func} is not callable")
            
        if not isinstance(file_type, (str, list)):
            raise TypeError(f"{file_type} must be passed as either string or list")
                
        if isinstance(file_type, list):
            for ft in set(file_type):
                if not isinstance(ft, str):
                    raise TypeError(f"{ft} must be passed as a string")
                self._mapp[ft] = func
        else:
            self._mapp[file_type] = func
        
    def add_functions(self, func_ftype_dict):
        """
        Function for adding multiple loader function and file type mappings.
        
        Function that allows to add multiple loader function and file type 
        mappings, by iteativley calling _add method.
        
        Parameters
        ----------
        func_ftype_dict: Dict[callable : str | list]
            Dictionary with loading functions and extension_type(s) paris.
        
        Retruns
        -------
        None
        """
        if not isinstance(func_ftype_dict, dict):
            raise TypeError('func_ftype_dict must by dictonary type')
        for k, v in func_ftype_dict.items():
            self._add(k, v)
    
    def _inspect(self, function):
        """
        Private function for returning all of the parameters accepted by a loader function.
        
        Parameters
        ----------
        function: Callable
            Function which paramaters have to be retrived.
        
        Retruns
        -------
        odict_keys
            Collection of the paramaters accepted by the function.
        """
        return inspect.signature(function).parameters.keys()
    
    @lru_cache(maxsize=None)            
    def load(self, path, **kwargs):
        """
        Implementation of ABLoader interface.
        
        Function implementing ABLoader interface, delegating loading data 
        operations to al loader function based on the pre-defined file type,
        from a file specifed by a path-like string, istributing matching key-value 
        arguments to all of the available loader functions.
        
        Parameters
        ----------
        path: str
            path-like string pointing to an existing file.
        kwargs: dict
            Key, value arguments to be distributed to loader functions.
        
        Retruns
        -------
        obj
            object loaded by the delagete function.
        """
        f = self._mapp[Path(path).suffix]
        return f(path, **{k:v for k, v in kwargs.items() if k in self._inspect(f)})
    