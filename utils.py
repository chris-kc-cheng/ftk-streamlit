import calendar
import functools
import hashlib
import pickle
import inspect
import json
import redis
import os
from datetime import datetime, timezone
import streamlit as st
import toolkit as ftk


def format_table(s):
    tbl = s.groupby([(s.index.year), (s.index.month)]).sum()
    tbl = tbl.unstack(level=1).sort_index(ascending=False)
    tbl.columns = [calendar.month_abbr[m] for m in range(1, 13)]
    tbl['YTD'] = tbl.agg(ftk.compound_return, axis=1)
    return tbl.style.format('{0:.2%}')


@st.cache_resource
def get_redis():
    return redis.from_url(os.environ["REDIS_URL"])


def redis_cache(ttl=3600, namespace="ftk-streamlit"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r = get_redis()

            # Create deterministic cache key
            bound = inspect.signature(func).bind(*args, **kwargs)
            bound.apply_defaults()

            key_data = {
                "func": func.__name__,
                "args": bound.args,
                "kwargs": bound.kwargs,
            }

            raw_key = json.dumps(key_data, sort_keys=True, default=str)
            hashed = hashlib.sha256(raw_key.encode()).hexdigest()
            redis_key = f"{namespace}:{func.__name__}:{hashed}"

            # Try cache
            cached = r.get(redis_key)
            meta_key = f"{namespace}:meta:{func.__name__}:{hashed}"
            if cached:
                remaining = r.ttl(redis_key)
                if remaining > 0:
                    r.set(meta_key, json.dumps(
                        key_data, default=str).encode(), nx=True, ex=remaining)
                return pickle.loads(cached)

            # Compute result
            result = func(*args, **kwargs)

            # Store in Redis (data + readable metadata for cache inspector)
            r.setex(redis_key, ttl, pickle.dumps(result))
            key_data["cached_at"] = datetime.now(timezone.utc).isoformat()
            r.setex(meta_key, ttl, json.dumps(key_data, default=str).encode())
            return result

        return wrapper
    return decorator
