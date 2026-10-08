import os
from pathlib import Path
import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
    assert connection.execute("SELECT 6 * 7").fetchone() == (42,)
Path("workspace-proof.txt").write_text("Python package and PostgreSQL passed\n")
print("Installed Python package, PostgreSQL and workspace passed")
