import re

def dec_handler(path:str,func,method,routes):
        param_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        annotations = func.__annotations__
        defaults = func.__defaults__ or ()
        default_offset = len(param_names) - len(defaults)
        default_map = {param_names[i + default_offset]: defaults[i] for i in range(len(defaults))}
        routes[f"{method}"].append(url(path, param_names, annotations, default_map, func))
        return func

def mid_handler (middle_ware_method:str,func,middleware):
      if middle_ware_method in middleware:
            return "A middleware of the same name is already present"
      middleware[middle_ware_method]=func
      

def url(path, param_names, annotations, default_map, func):
    pattern = re.sub(r'{(\w+)}', r'(?P<\1>[^/]+)', path)
    compiled_pattern = re.compile(f'^{pattern}$')
    return (compiled_pattern, param_names, annotations, default_map, func)