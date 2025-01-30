"""
Background task handlers for agent operations
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from django.conf import settings

def run_in_background(func):
    """Decorator to run async functions in a background thread"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor(max_workers=getattr(settings, 'BACKGROUND_TASK_ASYNC_THREADS', 4)) as executor:
            future = executor.submit(lambda: asyncio.run(func(*args, **kwargs)))
            return future.result()
    return wrapper

def async_handler(func):
    """Decorator to handle async functions in DRF views"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

def stream_handler(generator_func):
    """Decorator to handle async generators in DRF views"""
    @wraps(generator_func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        async def run_generator():
            async for item in generator_func(*args, **kwargs):
                yield item
        
        return loop.run_until_complete(run_generator())
    return wrapper