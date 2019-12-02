import _ast


iterated = {_ast.List: list,
            _ast.Set: set,
            _ast.Tuple: tuple}


simple = [_ast.Str, _ast.Num]
data_types = [x for x in iterated.keys()] + simple

values_for_ast_type = {
    _ast.List: 'elts',
    _ast.Set: 'elts',
    _ast.Tuple: 'elts',
    _ast.Str: 's',
    _ast.Num: 'n'
}
