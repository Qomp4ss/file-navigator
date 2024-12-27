import os
from itertools import chain, filterfalse, groupby
from functools import lru_cache
from pathlib import Path
from . import matching
import inspect


class PathManager:
    
    def __init__(self, paths, reader = None):
        if isinstance(paths, tuple):
            self._paths = [paths]
        else:
            self._paths = paths
        self.matching_eng = matching
           
    def __len__(self):
        return len(self._paths)
                  
    def load(self, reader, **kwargs):
        return [reader.load(os.path.join(*p), kwargs) for p in self._paths]
    
    def select_paths(self, pattern, match_type = 'eq'):
        return self.__class__(
            list(
                filter(
                    lambda p: getattr(self.matching_eng, match_type)(p[0], pattern), 
                    self._paths
                    )
                )
            )
    
    @property
    def paths(self):
        return list(tuple(reversed(p)) for p in self._paths)

    def groupby(self, by):
        return {
            k:self.__class__(list(g)) for k, g in groupby(
                sorted(
                    self._paths, key= getattr(self, by)
                    ),  getattr(self, by)
                )
            }
    
    #Sorting functions   
    def path(self, it):
        return it[0]

    def name(self, it):
        return Path(it[1]).stem

    def ext(self, it):
        return Path(it[1]).suffix
      
        

class PathFinder:
    
    def __init__(self, init_dirs = None):
        self.directories = {}
        self.matching_eng = matching
        self.pm = PathManager

        
        if init_dirs is not None:
            self.add_dirs(init_dirs)
            
    def add_dir(self, directory, traverse_subdirs = False):
        if os.path.isdir(directory):
            self.directories[directory] = traverse_subdirs
        else:
            raise ValueError("Specified directory does not exist")
            
        if not (isinstance(traverse_subdirs, (bool, int)) and int(traverse_subdirs) <= 1):
            raise ValueError("'traverse_subdirs' argument must be bool or int: (0,1)")

            
    def del_dir(self, directory):
        del self.directories[directory]
        
    def add_dirs(self, directories):
        for k, v in directories.items():
            self.add_dir(k, v)
    
    def del_dirs(self, directories):
        if not hasattr(directories, "__iter__"):
            raise ValueError('"directories" argument must be iterable')
        for d in directories:
            self.del_dir(d)
            
    @lru_cache(maxsize=None)
    def _resolve_ext(self, string):
        if '.' in string:
            return string.replace('.', '')
        else:
            return string

          
    def _traverse_subdir(self, directory, name, ext, name_type, ext_type):
        return ((root, file) for root, _, files in os.walk(directory) 
                for file in files 
                if os.path.isfile(os.path.join(root, file))
                and getattr(self.matching_eng, ext_type)(self._resolve_ext(Path(file).suffix), ext)
                and getattr(self.matching_eng, name_type)(Path(file).stem, name))


                
    def _traverse_dir(self, directory, name, ext, name_type, ext_type):
        return ((directory, file)  for file in os.scandir(directory) 
                if os.path.isfile(os.path.join(directory, file))
                and getattr(self.matching_eng, ext_type)(self._resolve_ext(Path(file).suffix), ext)
                and getattr(self.matching_eng, name_type)(Path(file).stem, name))

    @lru_cache(maxsize=None)
    def _get_obj_func(obj):
        return ', '.join(
            i[0] for i in inspect.getmembers(obj, predicate=inspect.isfunction)
            )

    @lru_cache(maxsize=None)
    def find(self, name, ext, name_type = 'eq', ext_type = 'eq'):
        if not isinstance(name, str):
            raise ValueError('"name" argument must be string type')     
            
        if not isinstance(name, str):
            raise ValueError('"ext" argument must be string type')     
            
        if not hasattr(matching, name_type):
            raise ValueError(f'"name_type" argument must be one of {self._get_obj_func(matching)}')
            
        if not hasattr(matching, ext_type):
            raise ValueError(f'"name_type" argument must be one of {self._get_obj_func(matching)}')


        return self.pm(
                set(
                    filterfalse(
                        lambda path: path is False, 
                        chain.from_iterable(
                            [self._traverse_subdir(directory, 
                                                   name, self._resolve_ext(ext),  
                                                   name_type, ext_type) 
                             if traverse_subdirs 
                             else self._traverse_dir(directory, 
                                                     name, self._resolve_ext(ext),  
                                                     name_type, ext_type)
                             for directory, traverse_subdirs in self.directories.items()]
                            )
                        )
                    )
                )
            
    
