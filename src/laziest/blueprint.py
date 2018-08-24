""" logic for generating package structure and folders """
import os

from laziest import defaults


class PackageCreator(object):

    def __init__(self, name, path):
        self.package_name = name
        self.source_path = self._create_path(path)

    @staticmethod
    def _create_path(path):
        if os.path.isfile(path):
            raise ValueError("path {} is a file cannot create package, "
                             "please provide correct path to directory ")
        else:
            os.makedirs(path, exist_ok=True)

    def create_structure(self):
        """ create all files """
        project_dir = os.path.join(self.source_path, self.package_name)
        package_dir = os.path.join(self.source_path, self.package_name,
                                   self.package_name)
        os.makedirs(project_dir)
        os.makedirs(package_dir)

        for file_name in defaults.project_files:
            _file_path = os.path.join(package_dir, file_name)
            with open(_file_path, "w+") as _new_file:
                _new_file.writelines(eval("defaults.{}_content".format(
                    file_name)))
