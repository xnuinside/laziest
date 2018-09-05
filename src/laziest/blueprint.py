""" logic for generating package structure and folders """
import os
import subprocess
from laziest import defaults


class PackageCreator(object):
    """
    - keys: ['--req']
      help: "Create requirements.txt files for different dependencies types: all
            - generate all 3 files \n prod - generate only requirements.txt \n"
      default: prod
      choices: ["all", "prod", "dev", "test"]
"""

    def __init__(self, args):
        self.package_name = args.package_name
        self.rewrite = None
        if 'rewrite' in args:
            self.rewrite = args.rewrite
        self.target_dir = self._check_path_or_create(args.path)
        self.project_name = self.package_name if 'project' not in args \
            else args.package_name
        if args.check_pypi:
            self._check_pypi()
        self.source_dir = "" if 'source_dir' not in args else args.source_dir
        self.args = args

    def _check_path_or_create(self, path):
        if os.path.isfile(path):
            raise ValueError("path {} is a file cannot create package, "
                             "please provide correct path to directory ")
        elif os.path.isdir(path) and not self.rewrite:
            if os.listdir(path):
                raise ValueError("Directory {} not empty. "
                                 "Remove all files and dirs inside or provide "
                                 "'--rewrite' flag to rewrite files in directory")
        else:
            os.makedirs(path, exist_ok=True)
        return path

    def create_structure(self):
        """ create all files """
        project_dir = os.path.join(self.target_dir, self.project_name)
        package_dir = os.path.join(
            project_dir, self.source_dir if self.source_dir else "",
            self.package_name)

        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(package_dir, exist_ok=True)

        project_files = self._get_valid_project_files()

        for file_name in project_files:
            _file_path = os.path.join(project_dir, file_name)
            with open(_file_path, "w+") as _new_file:
                try:
                    _new_file.writelines(eval("defaults.{}_content".format(
                        file_name.replace(".", "_"))))
                except AttributeError:
                    _new_file.writelines("")

        project_dirs = self._get_valid_project_dirs()
        for dir_name in project_dirs:
            _dir_path = os.path.join(project_dir, dir_name)
            os.makedirs(_dir_path, exist_ok=True)

        with open(os.path.join(package_dir, defaults.INIT_FILE), "w+") as init_file:
            init_file.writelines(defaults.init_py_content)

        print("Project {} successful was created in path {}".format(self.project_name,
                                                                    self.target_dir))
        if not self.args.no_git:
            git_init = subprocess.Popen(['git', 'init', project_dir],
                                        stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            git_init.wait()
            print("Git init {}".format("successful"
                                       if git_init.returncode == 0 else "failed"))

    def _get_valid_project_files(self):
        pj_files = defaults.pj_files
        if self.args.no_tox:
            pj_files.pop(pj_files.index(defaults.TOX_FILE))
        if self.args.req is not 'prod':
            for name in self.args.req.split(','):
                pj_files.append("{}-requirements.txt".format(name))

        return pj_files

    def _get_valid_project_dirs(self):
        pj_dirs = defaults.pj_dirs
        if self.args.no_docs:
            pj_dirs.pop(pj_dirs.index(defaults.DOC_DIR))
        return pj_dirs

    def _check_pypi(self):
        pip_search = subprocess.Popen(['pip', 'search', self.project_name],
                                      stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE)

        stdout_list = [line for line in pip_search.stdout.readlines()]
        pip_search.wait()
        if stdout_list:
            for elem in stdout_list:
                package_name = elem.split()[0].decode('utf-8')
                if package_name == self.project_name:
                    raise ValueError("Project with same name exist on PyPi")
