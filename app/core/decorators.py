import time
from functools import wraps


def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = round((end - start) * 1000, 2)
        print(f"{func.__name__} took {duration} ms")
        return result

    return wrapper
