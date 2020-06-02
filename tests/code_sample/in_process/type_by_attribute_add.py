def parse_cookie_full(cookie):
    cookiedict = {}
    for chunk in cookie.split(';'):
        if '=' in chunk:
            key, val = chunk.split('=', 1)
        else:
            key, val = '', chunk
        key, val = key.strip(), val.strip()
        if key or val:
            cookiedict[key] = val
    return cookiedict
