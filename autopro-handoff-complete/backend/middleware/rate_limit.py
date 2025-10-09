# Minimal rate limit stub for FAKE_MODE

async def rate_limit_middleware(max_requests=100, time_window=60):
    async def middleware(request, call_next):
        return await call_next(request)
    return middleware
