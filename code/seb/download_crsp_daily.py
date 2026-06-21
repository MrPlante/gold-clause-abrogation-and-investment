"""
Download CRSP daily stock file (crsp.dsf) for 1926-1940, all stocks, from WRDS.

Connects to the WRDS PostgreSQL endpoint using psycopg3 with direct TLS
negotiation (sslnegotiation=direct) -- required because the local network drops
Postgres's plaintext SSLRequest preamble. The password is read from ~/.pgpass;
WRDS requires Duo 2FA, so the connection blocks until the push is approved.

Output: data/crsp/dsf_1926_1940.parquet
"""

import os
import sys
import time

import pandas as pd
import psycopg

OUT_PATH = "../../data/crsp/dsf_1926_1940.parquet"

COLUMNS = ["permno", "date", "ret", "retx", "prc", "vol",
           "shrout", "cfacpr", "cfacshr"]

QUERY = f"""
    select {", ".join(COLUMNS)}
    from crsp.dsf
    where date between '1926-01-01' and '1940-12-31'
    order by permno, date
"""

CONN = dict(
    host="wrds-pgdata.wharton.upenn.edu",
    port=9737,
    dbname="wrds",
    user="mrplante",
    sslmode="require",
    sslnegotiation="direct",
    connect_timeout=170,
)


def main():
    t0 = time.time()
    print("Connecting to WRDS (approve the Duo push)...", flush=True)
    try:
        con = psycopg.connect(**CONN)
    except Exception as e:
        print(f"CONNECT FAIL after {time.time()-t0:.1f}s ->",
              str(e).strip().splitlines()[-1])
        sys.exit(1)
    print(f"Connected after {time.time()-t0:.1f}s. Running query...", flush=True)

    df = pd.read_sql(QUERY, con)
    con.close()
    print(f"Fetched {len(df):,} rows, {df['permno'].nunique():,} permnos "
          f"({df['date'].min()} to {df['date'].max()}) in {time.time()-t0:.1f}s",
          flush=True)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    size_mb = os.path.getsize(OUT_PATH) / 1e6
    print(f"Saved: {OUT_PATH} ({size_mb:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
