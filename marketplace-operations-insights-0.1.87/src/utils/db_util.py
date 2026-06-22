import streamlit as st
from typing import Dict
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
from threading import Lock

conn = {}
conn_lock = Lock()

def adapt_numpy_int64(n):
    return AsIs(int(n))

register_adapter(np.int64, adapt_numpy_int64)

def query(query: str, params: Dict = None, ttl: int = 3600, db="redshift"):
    global conn
    # Fast path without lock
    if db not in conn:
        # Double-checked locking to avoid race conditions in multi-threaded contexts
        with conn_lock:
            if db not in conn:
                # cache up to a few connections; supports any [connections.<db>] in secrets.toml
                conn[db] = st.connection(db, type="sql", max_entries=4)

    # Convert all numpy.int64 in params to int
    if params:
        params = {k: int(v) if isinstance(v, np.int64) else v for k, v in params.items()}

    return conn[db].query(query, params=params, ttl=ttl)

def reset():
    global conn
    # close each connection
    for db in conn:
        conn[db].reset()
