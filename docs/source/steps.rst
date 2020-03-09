Simple example:

Left side
step -> var_name == arg_name
    \ -> var_name != arg_name

{'var_name': left_side; 'step': step}

Example:

key, new_var = key.strip(), val.strip()
new_var *= 4

steps:
    val: [{'var_name': new_var; 'step': val.strip()},
           {'var_name': new_var; 'step': *= 4}]

Contains var names dependencies

steps_dependencies:
    new_var: val


Intersections:

def vars_intersections_steps(key, val):
    key, new_var = key.strip(), val.strip()
    new_var *= 4
    alias_var = key + new_var
    return alias_var
