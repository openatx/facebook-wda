# coding: utf-8

import functools
import typing
import inspect


def inject_call(fn, *args, **kwargs):
    """
    Call function without known all the arguments

    Args:
        fn: function
        args: arguments
        kwargs: key-values
    
    Returns:
        as the fn returns
    """
    assert callable(fn), "first argument must be callable"

    st = inspect.signature(fn)
    fn_kwargs = {
        key: kwargs[key]
        for key in st.parameters.keys() if key in kwargs
    }
    ba = st.bind(*args, **fn_kwargs)
    ba.apply_defaults()
    return fn(*ba.args, **ba.kwargs)


def limit_call_depth(n: int):
    """
    n = 0 means not allowed recursive call
    """
    def wrapper(fn: typing.Callable):
        if not hasattr(fn, '_depth'):
            fn._depth = 0

        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            if fn._depth > n:
                raise RuntimeError("call depth exceed %d" % n)

            fn._depth += 1
            try:
                return fn(*args, **kwargs)
            finally:
                fn._depth -= 1
        
        _inner._fn = fn
        return _inner
    
    return wrapper


def main():
    @limit_call_depth(1)
    def foo(a):
        print("Foo:", a)
        if a == 2:
            return
        foo(a+1)

    foo(0)

if __name__ == "__main__":
    main()