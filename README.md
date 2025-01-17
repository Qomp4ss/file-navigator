# file-navigator
Flexible directory scanner, file path manager, and customizable file loader-all in one.
## Features
- **File Searching**: Locate files using simple equality and inclusion checks, as well as advanced string matching options like regular expressions and glob patterns. These matching options can be applied to both file names and extensions.

- **Filtering**: Filter file paths based on specific string patterns, enhancing the precision of your searches.

- **Grouping**: Organize file paths by file names, extensions, or root paths, with support for string pattern matching in each grouping option.

- **Extensible Interface**: Provides an extendable interface for developing custom data loader objects, complemented by a flexible loader factory to accommodate various data loading requirements.

- **Method Chaining**: Seamlessly chain methods to achieve your goals efficiently, enhancing code readability and fluency.

## Installation
### From Source:
`pip install git+https://github.com/Qomp4ss/file-navigator.git`

For specific instalations please use [VCS Support](https://pip.pypa.io/en/stable/topics/vcs-support/) as a reference

### From PyPi:
`pip install file-navigator`
  
## Examples
### Introduction 
To utilize all features of file-navigator, only two objects are needed:
+ __PathFinder__ - interface for all file-path operations (adding/deleting directories, find, groupby, select_paths)
+ __ABLoader__ - interface for creating custom Loader objects, which must be injected into PathFinder.load method

Additionally the package contains two Loder objects:
1. __BaseLoader__ - simple Loader factory that implements ABLoader interface allowing to dynamically create loader objects, 
based on a dictionary with loading functions and extension_type(s) pairs
2. __PDLoader__ - implementation of BaseLoader class adapting **pandas reader functions** for loading data. 

### Prerequisites
Example usecases, aprat from __PathFinder__ will be also utilizing PDLoader, to load tabular data:

```python
from file_navigator import PathFinder
from file_navigator import PDLoader
```

Additionaly the following directory structure in a D drive will be assumed:
```
CURRENCIES
│   Portfloio.xlsx
│   Porfolio Forecast.xlsx
│
└───APAC
│   │   xagjpy.txt
│   │   xaujpy.txt
│   │
│   └───Calculations
│       │   transformations.csv
│       │   cov_matrix.csv      
│   
└───EMEA
    │   chfeur.txt
    │   chfgbp.txt
    │   eurgbp.txt
```

---
### Example 1. Shallow search
Finding and loading xagjpy.txt and xaujpy.txt files from D:\CURRENCIES\APAC directory
```python
>>> path_finder_shallow = PathFinder({r'D:\CURRENCIES\APAC':False})
>>> apac_pairs = path_finder_shallow.find('.*', 'txt', 'regex', 'eq').load(PDLoader)
```
```python
>>> apac_pairs[0].head()
```
|    | TICKER  |   PER |   DATE |   TIME |   OPEN |   HIGH |   LOW |   CLOSE |   VOL |   OPENINT |
|---:|:-----------|--------:|---------:|---------:|---------:|---------:|--------:|----------:|--------:|------------:|
|  0 | XAUJPY     |       5 | 20220817 |        0 |   238431 |   238471 |  238427 |    238446 |       0 |           0 |
|  1 | XAUJPY     |       5 | 20220817 |      500 |   238446 |   238446 |  238346 |    238346 |       0 |           0 |
|  2 | XAUJPY     |       5 | 20220817 |     1000 |   238346 |   238366 |  238323 |    238353 |       0 |           0 |
|  3 | XAUJPY     |       5 | 20220817 |     1500 |   238351 |   238373 |  238302 |    238325 |       0 |           0 |
|  4 | XAUJPY     |       5 | 20220817 |     2000 |   238325 |   238386 |  238318 |    238361 |       0 |           0 |
```python
>>> apac_pairs[1].head()
```
|    | TICKER   |   PER |   DATE |   TIME |   OPEN |   HIGH |   LOW |   CLOSE |   VOL |  OPENINT |
|---:|:-----------|--------:|---------:|---------:|---------:|---------:|--------:|----------:|--------:|------------:|
|  0 | XAGJPY     |       5 | 20220817 |        0 |  2704.16 |  2706.43 | 2704.13 |   2706.42 |       0 |           0 |
|  1 | XAGJPY     |       5 | 20220817 |      500 |  2706.42 |  2706.98 | 2704.18 |   2704.18 |       0 |           0 |
|  2 | XAGJPY     |       5 | 20220817 |     1000 |  2704.18 |  2704.76 | 2703.77 |   2704.33 |       0 |           0 |
|  3 | XAGJPY     |       5 | 20220817 |     1500 |  2704.31 |  2704.31 | 2703.04 |   2703.54 |       0 |           0 |
|  4 | XAGJPY     |       5 | 20220817 |     2000 |  2703.54 |  2704.65 | 2703.41 |   2704.07 |       0 |           0 |


### Example 2. Deep search 
Finding all files from Calculations directory and only Portfolio.xlsx file from CURRENCIES directory
```python
>>> portfolio = path_finder.find('^(?:(?!Forecast).)+$', '.xlsx|.csv', 'regex', 'regex')
>>> portfolio.paths
[('cov_matrix.csv', 'D:\\CURRENCIES\\APAC\\Calculations'),
 ('transformations.csv', 'D:\\CURRENCIES\\APAC\\Calculations'),
 ('Portfolio.xlsx', 'D:\\CURRENCIES')]
```


### Example 3. Deep search with group-by
Finding all txt files and grouping them by the folder they are in
```python
>>> path_finder = PathFinder({r'D:\CURRENCIES':True})
>>> pairs = path_finder.find('*', 'txt', 'glob').groupby('path')
>>> pairs['D:\\CURRENCIES\\APAC'].paths
[('xaujpy.txt', 'D:\\CURRENCIES\\APAC'),
 ('xagjpy.txt', 'D:\\CURRENCIES\\APAC')]
>>> pairs[ 'D:\\CURRENCIES\\EMEA'].paths
[('eurgbp.txt', 'D:\\CURRENCIES\\EMEA'),
 ('chfgbp.txt', 'D:\\CURRENCIES\\EMEA'),
 ('chfeur.txt', 'D:\\CURRENCIES\\EMEA')]

```


### Example 4. Deep search with filtering and group-by 
Loading all txt and csv files, grouping them by extension and filtering txt files from APAC
```python
>>> text_files = path_finder.find('*', '.txt|.csv', 'glob', 'regex').groupby('ext')
>>> csv_files = text_files['.csv']
>>> csv_files.paths
[('transformations.csv', 'D:\\CURRENCIES\\APAC\\Calculations'),
 ('cov_matrix.csv', 'D:\\CURRENCIES\\APAC\\Calculations')]
>>> txt_EMEA_files = text_files['.txt'].select_paths('EMEA', 'isin')
>>> txt_EMEA_files.paths
[('eurgbp.txt', 'D:\\CURRENCIES\\EMEA'),
 ('chfgbp.txt', 'D:\\CURRENCIES\\EMEA'),
 ('chfeur.txt', 'D:\\CURRENCIES\\EMEA')]
```
---

## License
[MIT](LICENSE)