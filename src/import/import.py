import calendar
from collections import Counter
from datetime import datetime
from itertools import chain
from pathlib import Path
from tqdm import tqdm
import argparse
import random
import pandas as pd
from pyalex import Works, Authors
import duckdb

    
def paper_db(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS paper (
            ego_aid VARCHAR,
            ego_display_name VARCHAR,
            wid VARCHAR,
            pub_date DATE,
            pub_year INT,
            doi VARCHAR,
            title VARCHAR,
            work_type VARCHAR,
            primary_topic VARCHAR,
            authors VARCHAR,
            cited_by_count INT,
            ego_position VARCHAR,
            ego_institution VARCHAR,
            PRIMARY KEY(ego_aid, wid)
        )
    """)

    if aid is not None:
        return (con.execute("SELECT ego_aid, wid FROM paper WHERE ego_aid = ?", (aid,)).fetchall())

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="JSONlines file with urls and hashes",
        required=True,
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

dyn_sync_networks = Works().filter(topics= {"id":"t11187"})
works_dyn_sync = []
for w in chain(*dyn_sync_networks.paginate(per_page=200)):
    works_dyn_sync.append(w)

df_dyn=pd.DataFrame(works_dyn_sync)
df_dyn.to_parquet("dyn_sync_networks.parquet")

stat_mech_networks = Works().filter(topics= {"id":"t10064"})
works_stat_mech = []
for w in chain(*stat_mech_networks.paginate(per_page=200)):
    works_stat_mech.append(w)
df_stat=pd.DataFrame(works_stat_mech)
df_stat.to_parquet("stat_mech_networks.parquet")


def main():
    args = parse_args()
    # update_author_age = True
    update_author_age = args.update
    con = duckdb.connect(str(args.output / "oa_data_raw.db") )

    assert args.input.exists(), "Input file does not exist"


    query = """
        INSERT INTO author
        (aid, display_name, institution, pub_year, first_pub_year, last_pub_year, author_age)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (aid, pub_year) 
        DO UPDATE SET
            institution = COALESCE(EXCLUDED.institution, author.institution),
            first_pub_year = COALESCE(EXCLUDED.first_pub_year, author.first_pub_year)
    """
    
    con.executemany(query, dedup_author_df.values.tolist())
        
    # Commit and close DB connection
    con.commit()
    con.close()

if __name__ == "__main__":
    main()
