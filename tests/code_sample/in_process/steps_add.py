def vars_intersections_steps(key, val):
    key, new_var = key.strip(), val.strip()
    new_var *= 4
    alias_var = key + new_var
    return alias_var

