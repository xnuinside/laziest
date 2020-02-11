import os
from typing import List
from glob import glob


INIT_FILE = '__init__.py'


class FilteredPaths:
    """ class to read files with paths to ignore (.gitignore, .dockerignore) and create full list of ignored paths
    TODO: make correct work with ** ignore_paths and ignore names
    """
    def __init__(self, ignore_files=None, ignore_paths=None, ignore_names=None):

        self.ignore_files = ignore_files or []
        self.ignore_paths = ignore_paths or []
        self.ignore_names = ignore_names or []
        if self.ignore_files:
            for ign_f in self.ignore_files:
                self._read_ignore_file(ign_f)

    def _read_ignore_file(self, file_path):
        """ append paths from ignore file to ignore_paths list """
        with open(file_path) as ignore_file:
            for line in ignore_file.readlines():
                paths = [x for x in glob(os.path.abspath(line.replace("\n", "")))]
                [self.ignore_paths.append(_path) for _path in paths]


class PathWalker(object):
    """
        work with target path,
            get package from the path and all py files or decide that this is stand alone
            py

        ignore names from ignore_names list
    """
    def __init__(self, path: str,
                 fp: FilteredPaths,
                 recursive: bool = False) -> None:
        # TODO: add ignore files, subdirs
        self.path = os.path.abspath(path)
        self.fp = fp
        print(recursive)
        self.recursive = recursive
        self.python_files = self.found_python_files()

    def found_python_files(self) -> List[str]:
        """ found all python files, depend on passed path """
        if os.path.isdir(self.path):
            self.path = self.path+"/*" if not self.recursive else self.path+"/**"
            print(self.path)
        paths = sorted([path for path in glob(self.path, recursive=self.recursive) if path.endswith('.py')])
        ignore_paths = []
        for path in paths:
            for ignore_path in self.fp.ignore_paths:
                if path.startswith(ignore_path):
                    ignore_paths.append(path)
                    break
            else:
                if os.path.basename(path) in self.fp.ignore_names:
                    ignore_paths.append(path)
        paths = [x for x in paths if x not in ignore_paths]
        return paths
