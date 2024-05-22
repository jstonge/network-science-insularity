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
    input_dir = Path("data/by_year")
    output_dir = args.output
    
    for year in range(1994, 2010):
        df = pd.read_parquet(input_dir / f"{topic_id}_{year}.parquet")
        df = df[df.language == 'en']
        
        output_dir = output_dir / topic_id; output_dir.mkdir(exist_ok=True)
        output_dir = output_dir / topic_id; output_dir.mkdir(exist_ok=True)

        # For each paper in that year for a given topic
        for i,row in tqdm(df.iterrows(), total=len(df)):
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

            with open(output_dir / f"{row.id.split('/')[-1]}.json", "w") as f:
                json.dump(out, f)


if __name__ == "__main__":
    main()
