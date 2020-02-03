import astor
print(
astor.dump_tree(astor.parse_file('/Users/jvolkova/laziest/laziest/ast_example.py')))