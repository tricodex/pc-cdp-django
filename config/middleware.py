"""
Custom middleware for handling async operations
"""
import asyncio
from functools import partial
from django.http import HttpResponse
from django.core.handlers.asgi import ASGIRequest
from channels.db import database_sync_to_async

class AsyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._async_capable = asyncio.iscoroutinefunction(get_response)

    async def __call__(self, request):
        if self._async_capable:
            return await self.get_response(request)
        return await database_sync_to_async(self.get_response)(request)

    async def process_request(self, request):
        if hasattr(self, 'process_request_async'):
            return await self.process_request_async(request)
        return None

    async def process_response(self, request, response):
        if hasattr(self, 'process_response_async'):
            return await self.process_response_async(request, response)
        return response