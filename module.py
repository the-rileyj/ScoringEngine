import importlib
import pkgutil
import sys
import inspect
import re

def load_module(module_str):
    """
    Get the module specified by the given string.
    
    Arguments:
        module_str (str): String representing the module's import path

    Returns:
        Module: The module represented by the string
    """
    module = importlib.import_module(module_str)
    return module


def load_obj(function_str):
    """
    Get the object specified by the given string.
    
    Arguments:
        obj_str (str): String representing the object's import path

    Returns:
        Object: The object represented by the string
    """
    parts = function_str.split('.')
    module = load_module('.'.join(parts[:-1]))
    obj = getattr(module, parts[-1])
    return obj
   

def get_functions(module):
    """
    Get the names of all of the functions in the given module.

    Arguments:
        module (Module): A python module

    Returns:
        List(str): A list of function names
    """
    functions = []
    for attr_str in dir(module):
        attr = getattr(module, attr_str)
        if inspect.isfunction(attr):
            functions.append(attr_str)
    return functions

def get_functions_below(module):
    """
    Get all of the functions below the given module.

    Arguments:
        module (Module): A python module

    Returns:
        List(str): A list of function paths
    """
    functions = get_functions(module)
    if hasattr(module, '__path__'):
        for path, name, ispkg in pkgutil.iter_modules(module.__path__):
            next_module = load_module('%s.%s' % (module.__name__, name))
            funcs_below = get_functions_below(next_module)
            funcs_below = ['%s.%s' % (name, f) for f in funcs_below]
            functions.extend(funcs_below)
    return functions


def get_classes(module):
    """
    Get the names of all of the classes in the given module.

    Arguments:
        module (Module): A python module

    Returns:
        List(str): A list of class names
    """
    classes = []
    for attr_str in dir(module):
        attr = getattr(module, attr_str)
        if inspect.isclass(attr):
            classes.append(attr_str)
    return classes


def get_classes_matching(module, regexp):
    """
    Get the names of all of the classes in the given module which match the given regular expression.

    Arguments:
        module (Module): A python module
        regexp (RegExp): A regular expression

    Returns:
        List(str): A list of class names
    """
    classes = get_classes(module)
    mclasses = [c for c in classes if re.match(regexp, c)]
    return mclasses


def get_classes_below_matching(module, regexp):
    """
    Get the names of all of the classes below the given module which match the given regular expression.

    Arguments:
        module (Module): A python module
        regexp (RegExp): A regular expression

    Returns:
        List(str): A list of class names
    """
    classes = get_classes_matching(module, regexp)
    if hasattr(module, '__path__'):
        for path, name, ispkg in pkgutil.iter_modules(module.__path__):
            next_module = load_module('%s.%s' % (module.__name__, name))
            classes_below = get_classes_below_matching(next_module, regexp)
            classes.extend(classes_below)
    return classes


if __name__ == '__main__':
    module = load_module(sys.argv[1])
    functions = get_functions_below(module)
    classes = get_classes(module)
    mclasses = get_classes_below_matching(module, r'.+PollInput')
    print(functions)
    print(classes)
    print(mclasses)

