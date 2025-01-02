import os
from itertools import chain, filterfalse, groupby
from functools import lru_cache, partial
from pathlib import Path
from . import matching
import inspect
from .abc_loader import ABLoader



class _PathManager:
    """Private class for file path operations.
    
    Parameters:
        paths (List[Tuple[str, str]]): Two element Tuple or List of Tuples, 
            containg strings representing a file path and file name combined 
            with file extention.
        
    Attributes:
        paths (List[Tuple[str, str]]): Returns the list of the paths parameter,
            that the class was instatiated with in reversed order (file name is 
            the 1st item in the tuple istead of file path).
        matching_eng (matching): Class with the matching functions.
        
    Methods:
        select_paths (patter: str, match_type: str): Allows to filter the file paths 
            based on the given pattern and matching function from matching_eng.
            Default match type is equality check: 'eq'. 
            The method returns new instance of _PathManager.
        groupby (by: str, pattern: str, match type: str): Allows to group 
            the paths besed on following path elements: extention, name and path.
            Each of the grouping keys support also mattching by pattern 
            and mattching functions function from matching_eng.
            The method returns dictionary with group key and new instance of _PathManager
            istantiated with group values.
        load (Loader, **kwargs): Loads data from the file specided by single path.
        path (pattern:str, match_type:str, it): Key funtion for grouping paths
            by file path.
        name (pattern:str, match_type:str, it): Key funtion for grouping paths
            by file name.
        ext (pattern:str, match_type:str, it): Key funtion for grouping paths
            by file type.
    """   
    def __init__(self, paths):
        if isinstance(paths, tuple):
            self._paths = [paths]
        else:
            self._paths = paths
        self.matching_eng = matching
           
    def __len__(self):
        return len(self._paths)
                  
    def load(self, loader, **kwargs):
        """"
        Loads data from the file specided by single path.
        
        This method uses dependecy injection to leverage an object following 
        abc_Loader.ABLoader interface, to load data from all of the paths,
        that the _PathManager was instantiated with.
        
        Parameters
        ----------
        loader: type[abc_Loader.ABLoader]
            Object that have load method defined.
        kwargs: dict
            Key Value parameters that are supported by the loader object.
            
        Returns
        -------
        list
            List of the loaded data objects, e.g. pandas DataFrames.
        """
        if not isinstance(loader, ABLoader):
            raise TypeError("Incorrect Loader type. It must be ABLoader type")
        return [loader.load(os.path.join(*p), **kwargs) for p in self._paths]
    
    def select_paths(self, pattern, match_type = 'eq'):
        """"
        Filters file paths based on a specifed pattern and creates new object.
        
        This method allows to filter file paths based on a given pattern
        that is supported by the types defined in matching module.
        
        Parameters
        ----------
        pattern: str
            String that can be matched with a file path.
        match_type: str
            String representing a matching function from the matching module.
            
        Returns
        -------
        _PathManager
            New instance of _PathManager with filtered paths.
        """
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
        """
        Returns list with file paths and file names in reversed order.
        """
        return list(tuple(reversed(p)) for p in self._paths)

    def groupby(self, by, pattern = None, match_type = 'eq'):
        """
        Groups paths by specifed part and pattern.
        
        This function allows to group paths by a specifed part defined by 
        Key function (file path, file name and file type) as well as specifed 
        pattern that is supported by the types defined in matching module. 
        Function returns a dictionary with keys defined by Key function 
        and values which are new instances of _PathManager.
        
        Parameters
        ----------
        by: str
            String representing a Key function (path, name, ext).
        pattern: str
            String that can be matched with a file path part.
        match_type: str
            String representing a matching function from the matching module.
            
        Returns
        -------
        dict
            Dictionary with keys defined by a Key function and values which are 
            new instances of _PathManager.
        """
        return {
            k:self.__class__(list(g)) for k, g in groupby(
                sorted(
                    self._paths, key= partial(getattr(self, by), pattern, match_type)
                    ),   partial(getattr(self, by), pattern, match_type)
                )
            }
    
    #Sorting functions   
    def path(self, pattern, match_type, it):
        """
        Key function representing file path.
        
        This function returns a path file part of a single path item.
        
        Parameters
        ----------
        pattern: str
            String that can be matched with a file path.
        match_type: str
            String representing a matching function from the matching module.
            
        Returns
        -------
        str
            A path file.
        """
        if pattern is None:
            return it[0]
        else:
            return getattr(self.matching_eng, match_type)(it[0], pattern)

    def name(self, pattern, match_type, it):
        """
        Key function representing file name.
        
        This function returns a file name part of a single path item.
        
        Parameters
        ----------
        pattern: str
            String that can be matched with a file name (without file type).
        match_type: str
            String representing a matching function from the matching module.
            
        Returns
        -------
        str
            A file name (without file type).
        """
        if pattern is None:
            return Path(it[1]).stem
        else:
            return getattr(self.matching_eng, match_type)(Path(it[1]).stem, pattern)


    def ext(self, pattern, match_type, it):
        """
        Key function representing file type.
        
        This function returns a file type part of a single path item.
        
        Parameters
        ----------
        pattern: str
            String that can be matched with a file type.
        match_type: str
            String representing a matching function from the matching module.
            
        Returns
        -------
        str
            A file type.
        """
        if pattern is None:
            return Path(it[1]).suffix
        else:
            return getattr(self.matching_eng, match_type)(Path(it[1]).suffix, pattern)
        

      
        

class PathFinder:
    """Main class for navigating trough directories and fiding matching paths,
    supporting globing and regex patterns as well as equality and inclusion checks
    for file name and type separately"""    
    def __init__(self, init_dirs = None):
        self.directories = {}
        self.matching_eng = matching
        self.pm = _PathManager

        
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
    def _get_obj_func(self, obj):
        return ', '.join(
            i[0] for i in inspect.getmembers(obj, predicate=inspect.isfunction)
            )

    @lru_cache(maxsize=None)
    def find(self, name, ext, name_type = 'eq', ext_type = 'eq'):
        if not isinstance(name, str):
            raise TypeError('"name" argument must be string type')     
            
        if not isinstance(ext, str):
            raise TypeError('"ext" argument must be string type')     
            
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
            
    
