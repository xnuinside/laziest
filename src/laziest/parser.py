""" generator of test_*.py files"""


class GeneratorTestsFiles(object):

    space4 = "    "
    header = "import unittest \n"
    footer = '\n\nif __name__ == "__main__":\n' \
             '{space4}unittest.main()'.format(space4=space4)

    def __init__(self, obj, file_name, path):
        self.path = "{}/test_{}".format(path, file_name)
        self.text_wrapper = """
class Test{}(unittest.TestCase): 
        """.format(obj.__name__)
        if isinstance(obj, object):
            self.objects_tests(obj)

    def objects_tests(self, obj):
        for each in obj.__dict__:
            if each != "__init__" and callable(obj.__dict__[each]):
                self.text_wrapper = self.text_wrapper + "\n" + \
                                    "{space4}def test_{funct_name}(self):\n" \
                                    "{space4}{space4}pass\n".format(
                                        space4=self.space4, funct_name=each)

    def generate_file(self):
        with open(self.path, "w+") as f:
            f.writelines([self.header, self.text_wrapper, self.footer])
