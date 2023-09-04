from contextlib import contextmanager

__debug_sql__ = False  # 

@contextmanager
def debug_sql(*args, **kwds):
    global __debug_sql__  # !
    # __debug_sql__ = __debug__ and True
    __debug_sql__ = True
    try:
        yield
    finally:
        __debug_sql__ = False

