import json
import pandas as pd
import streamlit as st
from utils import get_redis

NAMESPACE = "ftk-streamlit"


def format_ttl(seconds: int) -> str:
    if seconds < 0:
        return "No expiry"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    elif seconds < 86400:
        h, rem = divmod(seconds, 3600)
        return f"{h}h {rem // 60}m"
    else:
        d, rem = divmod(seconds, 86400)
        return f"{d}d {rem // 3600}h"


def scan_cache_keys(r):
    """Scan Redis for cache keys only, excluding meta keys."""
    keys = []
    cursor = 0
    while True:
        cursor, batch = r.scan(cursor, match=f"{NAMESPACE}:*", count=100)
        for k in batch:
            k_str = k.decode() if isinstance(k, bytes) else k
            # key format: {namespace}:{func_name}:{hash}
            # meta format: {namespace}:meta:{func_name}:{hash}
            parts = k_str.split(":", 2)
            if len(parts) >= 2 and parts[1] != "meta":
                keys.append(k)
        if cursor == 0:
            break
    return sorted(keys)


def get_meta(r, key_str: str) -> dict | None:
    """Retrieve metadata for a given cache key string."""
    parts = key_str.split(":", 2)
    if len(parts) != 3:
        return None
    ns, func_name, hash_part = parts
    meta_key = f"{ns}:meta:{func_name}:{hash_part}"
    raw = r.get(meta_key)
    if raw:
        try:
            return json.loads(raw.decode())
        except Exception:
            return None
    return None


def format_params(meta: dict | None) -> str:
    if meta is None:
        return "(unavailable)"
    args = meta.get("args", [])
    kwargs = meta.get("kwargs", {})
    parts = [repr(a) for a in args] + \
        [f"{k}={repr(v)}" for k, v in kwargs.items()]
    return ", ".join(parts) if parts else "(none)"


st.title("Cache Manager")

try:
    r = get_redis()
except Exception as e:
    st.error(f"Redis connection failed: {e}")
    st.info("Set the `REDIS_URL` environment variable to connect to Redis.")
    st.stop()

keys = scan_cache_keys(r)

with st.sidebar:
    if st.button("Clear All", type="primary", disabled=not keys, use_container_width=True):
        all_keys = r.keys(f"{NAMESPACE}:*")
        if all_keys:
            r.delete(*all_keys)
        st.rerun()
    if st.button("Refresh", use_container_width=True):
        st.rerun()

if not keys:
    st.info("No cached entries found.")
else:
    rows = []
    for key in keys:
        key_str = key.decode() if isinstance(key, bytes) else key
        parts = key_str.split(":", 2)
        func_name = parts[1] if len(parts) >= 2 else "unknown"
        meta = get_meta(r, key_str)
        rows.append({
            "Function": func_name,
            "Parameters": format_params(meta),
            "Cached At": meta.get("cached_at") if meta else None,
            "TTL": format_ttl(r.ttl(key)),
            "_key": key_str,
        })

    df = pd.DataFrame(rows)
    st.caption(
        f"{len(df)} entr{'y' if len(df) == 1 else 'ies'} — click column headers to sort, select rows to delete")

    selection = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        column_config={"_key": None},
    )

    selected_indices = selection.selection.rows
    if selected_indices:
        selected_keys = df.iloc[selected_indices]["_key"].tolist()
        with st.sidebar:
            if st.button(f"Delete Selected ({len(selected_indices)})", type="primary", use_container_width=True):
                for key_str in selected_keys:
                    parts = key_str.split(":", 2)
                    ns_part, fn_part, hash_part = (parts + ["", ""])[:3]
                    meta_key = f"{ns_part}:meta:{fn_part}:{hash_part}"
                    r.delete(key_str.encode(), meta_key.encode())
                st.rerun()
