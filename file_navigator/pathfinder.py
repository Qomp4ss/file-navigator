"""
Main module with PathFinder object
"""
import os
from itertools import chain, filterfalse, groupby
from functools import lru_cache, partial
from pathlib import Path
import inspect
from . import matching
from .abc_loader import ABLoader



class _PathManager:
    """
    Private class for file path operations.

    Parameters:
        paths (List[Tuple[str, str]]): Two-element Tuple or List of Tuples,
            containing path-like strings and file names combined with file extensions.

    Attributes:
        paths (List[Tuple[str, str]]): Returns the list of the paths attribute,
            that the class was instantiated with in reversed order (file name is
            the first item in the tuple instead of the file path).
        matching_eng (Type(matching)): Class with the matching functions.

    Methods:
        select_paths (pattern: str, match_type: str): Allows filtering of the file paths
            based on the given pattern and matching function from matching_eng.
            Default match type is equality check: 'eq'.
            The method returns a new instance of _PathManager.
        groupby (by: str, pattern: str, match_type: str): Allows grouping
            the paths based on the following path elements: extension, name, and path.
            Each of the grouping keys also supports matching by pattern
            and matching functions from matching_eng.
            The method returns a dictionary with the group key and a new instance of _PathManager
            instantiated with group values.
        load (Loader, **kwargs): Loads data from the file specified by a single path.
        path (pattern: str, match_type: str, it): Key function for grouping paths
            by file path.
        name (pattern: str, match_type: str, it): Key function for grouping paths
            by file name.
        ext (pattern: str, match_type: str, it): Key function for grouping paths
            by file type.
    """
    def __init__(self, paths):
        if len(paths) == 0:
            raise ValueError('"paths" parameter is empty.')

        if isinstance(paths, tuple):
            self._paths = [paths]
        else:
            self._paths = paths
        self.matching_eng = matching

    def __len__(self):
        return len(self._paths)

    def load(self, loader, **kwargs):
        """"
        Loads data from the file specified by a single path-like string.

        This method uses dependency injection to leverage an object following
        abc_Loader.ABLoader interface, to load data from all of the paths
        that the _PathManager was instantiated with.

        Parameters
        ----------
        loader: type[abc_Loader.ABLoader]
            Object that has a load method defined.
        kwargs: dict
            Key-value parameters that are supported by the loader object.

        Returns
        -------
        list
            List of the loaded data objects, e.g., pandas DataFrames.
        """
        if not isinstance(loader, ABLoader):
            raise TypeError("Incorrect Loader type. It must be ABLoader type")
        return [loader.load(os.path.join(*p), **kwargs) for p in self._paths]

    def select_paths(self, pattern, match_type = 'eq'):
        """"
        Filters path-like strings based on a specified pattern and creates a new object.

        This method allows filtering file paths based on a given pattern
        that is supported by the types defined in the matching module.

        Parameters
        ----------
        pattern: str
            String that can be matched with a file path.
        match_type: str, default='eq'
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
        Returns a list with file paths and file names in reversed order.
        """
        return list(tuple(reversed(p)) for p in self._paths)

    def groupby(self, by, pattern = None, match_type = 'eq'):
        """
        Groups paths by a specified part and pattern.

        This function allows grouping paths by a specified part defined by
        a key function (file path, file name, and file type) as well as a specified
        pattern that is supported by the types defined in the matching module.
        The function returns a dictionary with keys defined by the key function
        and values which are new instances of _PathManager.

        Parameters
        ----------
        by: str
            String representing a key function (path, name, ext).
        pattern: str, default=None
            String that can be matched with a file path part.
        match_type: str, default='eq'
            String representing a matching function from the matching module.

        Returns
        -------
        dict
            Dictionary with keys defined by a key function and values which are
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
    def path(self, pattern, match_type, iterable):
        """
        Key function representing file path.

        This function returns a file path part of a single path item.

        Parameters
        ----------
        pattern: str
            String that can be matched with a file path.
        match_type: str
            String representing a matching function from the matching module.

        Returns
        -------
        str
            A file path.
        """
        if pattern is None:
            return iterable[0]
        return getattr(self.matching_eng, match_type)(iterable[0], pattern)

    def name(self, pattern, match_type, iterable):
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
            return Path(iterable[1]).stem
        return getattr(self.matching_eng, match_type)(Path(iterable[1]).stem, pattern)


    def ext(self, pattern, match_type, iterable):
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
            return Path(iterable[1]).suffix
        return getattr(self.matching_eng, match_type)(Path(iterable[1]).suffix, pattern)





class PathFinder:
    """
    Main class for navigating through directories and finding files.

    Class for navigating through directories and finding matching file paths,
    supporting pattern matching as defined in the matching module, for file name 
    and file type respectively. Can be instantiated empty or with a dictionary
    with directories to be scanned.

    Attributes:
        directories (Dict): Empty dictionary to which directory path and flag
            for flat or deep scan key, value pairs will be added.
        matching_eng (Type(matching)): Class with the matching functions.
        pm (Type(_PathManager)): Private class for file path operations.

    Parameters:
        init_dirs (Dict[str: bool], default=None): Dictionary with path-like 
            string as key and bool value.

    Methods:
        add_dir (directory: str, traverse_subdirs: bool, default=False): Method
            for adding single key, value pair of directory path with a bool flag 
            indicating deep or flat scan.
        del_dir (directory: str): Method for removing single key, value pair of
            directory path with traverse_subdirs flag.
        add_dirs (directories: Dict[str: bool]): Method for appending
            a collection of directory path and traverse_subdirs flag pairs.
        del_dirs (directories: str | List[str]): Method for deleting a collection 
            of directory path and traverse_subdirs flag pairs.
        find (name: str, ext: str, name_type: str[default='eq'], ext_type: str[default='eq']):
            Method for iterating through all of the directories collection and matching 
            files based on defined file name and file type patterns, supported 
            by the matching_eng.
    """
    def __init__(self, init_dirs = None):
        self.directories = {}
        self.matching_eng = matching
        self.path_manager = _PathManager


        if init_dirs is not None:
            self.add_dirs(init_dirs)

    def add_dir(self, directory, traverse_subdirs = False):
        """
        Function for adding a directory entry.
        
        This function allows adding a single directory entry, validating whether
        the passed key is a valid directory.
        
        Parameters
        ----------
        directory: str
            Path-like string pointing to an existing directory.
        traverse_subdirs: bool, default=False
            Flag indicating whether all subdirectories of the passed directory should 
            be iterated over.
            
        Returns
        -------
        None        
        """
        if os.path.isdir(directory):
            if any(self._overlap(directory, traverse_subdirs)):
                raise ValueError(f"{directory} can't be added due to conflicting "\
                                "parent - child relationship with already added "\
                                f"directories: {', '.join(self._overlap(directory, traverse_subdirs))}")
            self.directories[directory] = traverse_subdirs
        else:
            raise ValueError("Specified directory does not exist")

        if not (isinstance(traverse_subdirs, (bool, int)) and int(traverse_subdirs) <= 1):
            raise TypeError("'traverse_subdirs' argument must be bool or int: (0,1)")

    @lru_cache(maxsize=128)
    def _overlap(self, directory, traverse_subdirs):
        return [d for d, t_s in self.directories.items() if (
            (
                (d in directory and t_s ) or (directory in d and traverse_subdirs)
                )
            and len(d) != len(directory)
            )]


    def del_dir(self, directory):
        """
        Function for removing a directory entry.
        
        This function allows the removal of a single directory entry. If the specified
        directory is not part of the directories collection, a KeyError is raised.
        
        Parameters
        ----------
        directory: str
            Path-like string pointing to a directory in the directories collection.
            
        Returns
        -------
        None
        """
        del self.directories[directory]

    def add_dirs(self, directories):
        """
        Function for adding multiple directory entries.
        
        This function allows adding multiple directory entries passed as a dictionary, 
        iteratively calling the add_dir method.
        
        Parameters
        ----------
        directories: Dict[str: bool]
            Dictionary containing Path-like strings pointing to existing 
            directories with a traverse_subdirs flag.
            
        Returns
        -------
        None
        """
        for k, v in directories.items():
            self.add_dir(k, v)

    def del_dirs(self, directories):
        """
        Function for removing multiple directory entries.
        
        This function allows removing multiple directory entries passed in a list, 
        iteratively calling the del_dir method.
        
        Parameters
        ----------
        directories: str | List[str]
            List containing path-like strings or a single string pointing to existing 
            directory entries.
            
        Returns
        -------
        None
        """
        if not isinstance(directories, (list, str)):
            raise TypeError('"directories" argument must be a list os strings or a string')
        for directory in directories:
            self.del_dir(directory)

    @lru_cache(maxsize=128)
    def _resolve_ext(self, string):
        """
        Private function for standardizing file type strings.

        Parameters
        ----------
        string: str
            File extension string to be standardized.

        Returns
        -------
        str
            Standardized file extension without the dot prefix.
        """
        if '.' in string:
            return string.replace('.', '')
        return string


    def _traverse_subdir(self, directory, name, ext, name_type, ext_type):
        """
        Private function for nested directory iteration and file matching.
        
        This function iterates through a single directory, including all subdirectories,
        trying to match all files based on the specified name and file type patterns. 
        
        Parameters
        ----------
        directory: str
            Path-like string pointing to an existing directory.
        name: str
            File name pattern to be matched.
        ext: str
            File type (file extension) pattern to be matched.
        name_type: str
            String representing a function in matching_eng for matching 
            the file name pattern.
        ext_type: str
            String representing a function in matching_eng for matching 
            the file type (extension) pattern.
        
        Returns
        -------
        Generator[Tuple[root[str], file[str]]]
            Generator containing a 2-element tuple with the root directory 
            and the matching file.
        """
        return ((root, file) for root, _, files in os.walk(directory)
                for file in files
                if os.path.isfile(os.path.join(root, file))
                and getattr(self.matching_eng, ext_type)(self._resolve_ext(Path(file).suffix), ext)
                and getattr(self.matching_eng, name_type)(Path(file).stem, name))



    def _traverse_dir(self, directory, name, ext, name_type, ext_type):
        """
        Private function for flat directory iteration and file matching.
        
        This function iterates through a single directory, trying to match 
        all files based on the specified name and file type patterns. 
        
        Parameters
        ----------
        directory: str
            Path-like string pointing to an existing directory.
        name: str
            File name pattern to be matched.
        ext: str
            File type (file extension) pattern to be matched.
        name_type: str
            String representing a function in matching_eng for matching 
            the file name pattern.
        ext_type: str
            String representing a function in matching_eng for matching 
            the file type (extension) pattern.
        
        Returns
        -------
        Generator[Tuple[directory[str], file[str]]]
            Generator containing a 2-element tuple with the directory 
            and the matching file.
        """
        return ((directory, file)  for file in os.scandir(directory)
                if os.path.isfile(os.path.join(directory, file))
                and getattr(self.matching_eng, ext_type)(self._resolve_ext(Path(file).suffix), ext)
                and getattr(self.matching_eng, name_type)(Path(file).stem, name))

    @lru_cache(maxsize=128)
    def _get_obj_func(self, obj):
        """
        Private function to dynamically return a joined string of a list 
        containing all available functions in a specified object.
        
        Parameters
        ----------
        obj: Any
            The object whose functions will be retrieved.
        
        Returns
        -------
        str
            String of all object methods joined by commas.
        """
        return ', '.join(
            i[0] for i in inspect.getmembers(obj, predicate=inspect.isfunction)
            )

    @lru_cache(maxsize=128)
    def find(self, name, ext, name_type = 'eq', ext_type = 'eq'):
        """
        Function for finding files in defined directories.
        
        This function iterates through all directories in the directories attribute, 
        returning a new instance of the _PathManager class instantiated with all 
        unique matching files and paths pointing to them. Files are matched by both 
        file name and type patterns that are supported by matching_eng.
        
        Parameters
        ----------
        name: str
            File name pattern to be matched.
        ext: str
            File type (file extension) pattern to be matched.
        name_type: str, default='eq'
            String representing a function in matching_eng for matching 
            the file name pattern.
        ext_type: str, default='eq'
            String representing a function in matching_eng for matching 
            the file type (extension) pattern.
        
        Returns
        -------
        Type[_PathManager]
            New instance of the _PathManager class.
        """
        if not isinstance(name, str):
            raise TypeError('"name" argument must be string type')

        if not isinstance(ext, str):
            raise TypeError('"ext" argument must be string type')

        if not hasattr(matching, name_type):
            raise ValueError(f'"name_type" argument must be one of {self._get_obj_func(matching)}')

        if not hasattr(matching, ext_type):
            raise ValueError(f'"name_type" argument must be one of {self._get_obj_func(matching)}')

        if len(self.directories) == 0:
            raise ValueError('There are no dictionaries to be searched.')


        return self.path_manager(
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
