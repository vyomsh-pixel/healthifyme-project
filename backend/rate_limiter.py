import time
from datetime import datetime, timezone
import logging
from fastapi import Request, Header, HTTPException
from backend.database import database
from backend.security import token_hash

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests: int, window: int, by_user: bool = False):
        self.requests = requests
        self.window = window
        self.by_user = by_user

    def __call__(self, request: Request, authorization: str | None = Header(default=None)):
        key = None
        if self.by_user and authorization and authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ")
            key = f"user:{token_hash(token)}"
        
        if not key:
            client_ip = request.client.host if request.client else "127.0.0.1"
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()
            key = f"ip:{client_ip}"
            
        endpoint = request.url.path
        
        now = time.time()
        window_start_ts = now - (now % self.window)
        window_start = datetime.fromtimestamp(window_start_ts, tz=timezone.utc)
        
        try:
            with database() as conn:
                query = """
                    INSERT INTO rate_limits (key, endpoint, window_start, count)
                    VALUES (%(key)s, %(endpoint)s, %(window_start)s, 1)
                    ON CONFLICT (key, endpoint, window_start) 
                    DO UPDATE SET count = rate_limits.count + 1
                    RETURNING count;
                """
                cursor = conn.conn.cursor()
                cursor.execute(query, {
                    "key": key,
                    "endpoint": endpoint,
                    "window_start": window_start
                })
                result = cursor.fetchone()
                current_count = result["count"] if result else 1
                
                # Cleanup old windows occasionally (10% chance per request)
                if int(now) % 10 == 0:
                    cleanup_query = "DELETE FROM rate_limits WHERE window_start < %(cleanup_time)s"
                    cleanup_time = datetime.fromtimestamp(now - (self.window * 2), tz=timezone.utc)
                    cursor.execute(cleanup_query, {"cleanup_time": cleanup_time})
                    
                if current_count > self.requests:
                    raise HTTPException(status_code=429, detail="Too Many Requests")
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Rate limiter database error, failing open: {e}")
