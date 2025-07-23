# coding: utf-8

import pytest
import threading
import time
from unittest.mock import Mock

from wda.utils import limit_call_depth, inject_call, convert, AttrDict


class TestLimitCallDepth:
    """Test cases for the limit_call_depth decorator"""
    
    def test_basic_function_call(self):
        """Test that basic function calls work within the limit"""
        @limit_call_depth(2)
        def simple_function(x):
            return x * 2
        
        result = simple_function(5)
        assert result == 10
    
    def test_recursive_call_within_limit(self):
        """Test recursive calls that stay within the allowed depth"""
        @limit_call_depth(3)
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        
        # This should work as recursion depth is 3: factorial(3) -> factorial(2) -> factorial(1)
        result = factorial(3)
        assert result == 6
    
    def test_recursive_call_exceeds_limit(self):
        """Test that recursive calls exceeding the limit raise RuntimeError"""
        @limit_call_depth(2)
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        
        # This should fail as recursion depth exceeds 2
        with pytest.raises(RuntimeError, match="call depth exceed 2"):
            factorial(5)
    
    def test_zero_depth_limit(self):
        """Test that n=0 means no recursive calls are allowed"""
        @limit_call_depth(0)
        def recursive_function(n):
            if n <= 0:
                return 1
            return recursive_function(n - 1)
        
        # Direct call should work
        result = recursive_function(0)
        assert result == 1
        
        # Recursive call should fail immediately
        with pytest.raises(RuntimeError, match="call depth exceed 0"):
            recursive_function(1)
    
    def test_multiple_independent_calls(self):
        """Test that multiple independent calls don't interfere with each other"""
        @limit_call_depth(1)
        def simple_function(x):
            return x + 1
        
        # Multiple independent calls should all work
        assert simple_function(1) == 2
        assert simple_function(2) == 3
        assert simple_function(3) == 4
    
    def test_nested_calls_different_functions(self):
        """Test nested calls between different decorated functions"""
        @limit_call_depth(1)
        def function_a(x):
            if x > 0:
                return function_b(x - 1)
            return x
        
        @limit_call_depth(1)
        def function_b(x):
            return x * 2
        
        # This should work as each function has its own depth counter
        result = function_a(1)
        assert result == 0
    
    def test_threading_isolation(self):
        """Test that call depth counters are isolated between threads"""
        @limit_call_depth(1)
        def thread_function(n, results, thread_id):
            if n > 0:
                # This recursive call should be allowed in each thread independently
                return thread_function(n - 1, results, thread_id)
            results[thread_id] = "success"
            return "done"
        
        results = {}
        threads = []
        
        # Create multiple threads that make recursive calls
        for i in range(3):
            thread = threading.Thread(
                target=lambda tid=i: thread_function(1, results, tid)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should have succeeded
        assert len(results) == 3
        for i in range(3):
            assert results[i] == "success"
    
    def test_exception_resets_depth(self):
        """Test that exceptions properly reset the call depth"""
        @limit_call_depth(2)
        def function_with_exception(n):
            if n == 1:
                raise ValueError("Test exception")
            if n > 0:
                return function_with_exception(n - 1)
            return "success"
        
        # First call should raise the exception
        with pytest.raises(ValueError, match="Test exception"):
            function_with_exception(2)
        
        # After exception, depth should be reset and new calls should work
        result = function_with_exception(0)
        assert result == "success"
    
    def test_function_preserves_metadata(self):
        """Test that the decorator preserves function metadata"""
        @limit_call_depth(1)
        def documented_function(x, y=10):
            """This is a test function with documentation"""
            return x + y
        
        # Check that functools.wraps preserved the metadata
        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a test function with documentation"
        
        # Check that the function still works normally
        assert documented_function(5) == 15
        assert documented_function(5, y=20) == 25
    
    def test_complex_recursion_scenario(self):
        """Test a more complex recursion scenario"""
        @limit_call_depth(5)
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)
        
        # This should work as max depth for fib(5) is 5
        result = fibonacci(5)
        assert result == 5  # fib(5) = 5
        
        # This should fail as fib(10) would exceed depth 5
        with pytest.raises(RuntimeError, match="call depth exceed 5"):
            fibonacci(10)


class TestInjectCall:
    """Test cases for the inject_call function"""
    
    def test_inject_call_basic(self):
        """Test basic inject_call functionality"""
        def test_func(a, b, c=3):
            return a + b + c
        
        result = inject_call(test_func, 1, 2, c=4, extra_arg=999)
        assert result == 7  # 1 + 2 + 4
    
    def test_inject_call_with_defaults(self):
        """Test inject_call with default parameters"""
        def test_func(a, b=10, c=20):
            return a + b + c
        
        result = inject_call(test_func, 5, c=15)
        assert result == 30  # 5 + 10 + 15
    
    def test_inject_call_invalid_function(self):
        """Test inject_call with non-callable argument"""
        with pytest.raises(AssertionError):
            inject_call("not_a_function", 1, 2, 3)


class TestAttrDict:
    """Test cases for the AttrDict class"""
    
    def test_attr_dict_basic(self):
        """Test basic AttrDict functionality"""
        d = AttrDict({"name": "test", "value": 42})
        
        assert d.name == "test"
        assert d.value == 42
        assert d["name"] == "test"
        assert d["value"] == 42
    
    def test_attr_dict_missing_attribute(self):
        """Test AttrDict with missing attributes"""
        d = AttrDict({"name": "test"})
        
        with pytest.raises(AttributeError):
            _ = d.missing_attr
        
        # But dictionary access should raise KeyError
        with pytest.raises(KeyError):
            _ = d["missing_key"]


class TestConvert:
    """Test cases for the convert function"""
    
    def test_convert_basic(self):
        """Test basic convert functionality"""
        original_dict = {"name": "test", "value": 42}
        result = convert(original_dict)
        
        assert isinstance(result, AttrDict)
        assert result.name == "test"
        assert result.value == 42
    
    def test_convert_nested_dict(self):
        """Test convert with nested dictionary"""
        original_dict = {
            "user": {"name": "John", "age": 30},
            "settings": {"theme": "dark"}
        }
        result = convert(original_dict)
        
        assert isinstance(result, AttrDict)
        assert result.user == {"name": "John", "age": 30}
        assert result.settings == {"theme": "dark"}
