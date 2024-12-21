from abc import ABC, abstractmethod
import inspect
from pathlib import Path

class ABLoader(ABC):
    
    @abstractmethod
    def load(self, path, kwargs):
        raise NotImplementedError("This have to be implemented")

class BaseLoader(ABLoader):
    
    def __init__(self, func_ftype_dict = None):
        self._mapp = {}
        if func_ftype_dict is not None:
            self.add_functions(func_ftype_dict)
            
    def _add(self, func, file_type):
        
        if not callable(func):
            raise ValueError(f"{func} is not callable")
            
        if not isinstance(file_type, (str, tuple, list)):
            raise ValueError(f"{file_type} must be passed as either string, tuple or list")
                
        if isinstance(file_type, (list, tuple)):
            for ft in set(file_type):
                self._mapp[ft] = func
        else:
            self._mapp[file_type] = func
        
    def add_functions(self, func_ftype_dict):
        for k, v in func_ftype_dict.items():
            self._add(k, v)
    
    def _inspect(self, function):
        return inspect.signature(function).parameters.keys()
                
    def load(self, path, kwargs):
        f = self._mapp[Path(path).suffix]
        return f(path, **{k:v for k, v in kwargs.items() if k in self._inspect(f)})
    