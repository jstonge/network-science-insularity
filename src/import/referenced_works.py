from itertools import chain
import pandas as pd
from pyalex import Works, Authors
from time import sleep
from tqdm import tqdm
import requests
from collections import Counter
import json
from pathlib import Path
import requests
import argparse

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-t", "--topic", type=Path, help="output directory", required=True
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

def main():  
    """
    We make many api calls... #articles x #referenced works by article
    So in 2018 there was 6000 articles. If they have 100 references on average,
    that's 600,000 api calls. Perhaps it would be better to run this on our end.
    """
    args=parse_args()      
    topic_id = args.topic

    # topic_id='t11270'
    input_dir = Path("data") / "by_year" / topic_id
    output_dir = Path('data/ref_works_by_year')
    output_dir = args.output
    
    output_dir = output_dir / topic_id
    output_dir.mkdir(exist_ok=True)

    for year in range(1994, 2010):
        # year=1994
        yearly_out_dir = output_dir / str(year) 
        yearly_out_dir.mkdir(exist_ok=True)

        df = pd.read_parquet(input_dir / f"{topic_id}_{year}.parquet")
        df = df[df.language == 'en']
        
        done_rows = len(list(yearly_out_dir.glob("*.json")))
        if done_rows == len(df):
            print(f"Skipping year {year}")
            continue

        # For each paper in that year for a given topic
        for i,row in tqdm(df.iterrows(), total=len(df)):

            out_f = yearly_out_dir / f"{row.id.split('/')[-1]}.json"
            
            # check if already done. 
            if out_f.exists():
                print(f"Skip id {row.id}")
                continue

            # get works reference by that paper
            w = Works()[row.id]
            ref_works = w.get('referenced_works', []) if w else []
            if not ref_works:
                out = {}
            else:
                # get details of each referenced work
                ref_works_details = []
                for work in tqdm(ref_works, total=len(ref_works)):
                    
                    try:
                        details = Works()[work]
                        ref_works_details.append(details)
                    except requests.exceptions.HTTPError:
                        print(f"Error fetching {work}")
                        continue

                out = ref_works_details

            # for each paper, save details of all referenced works
            with open(out_f, "w") as f:
                json.dump(out, f)


if __name__ == "__main__":
    main()
