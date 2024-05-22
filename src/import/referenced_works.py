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
        "-i", "--input", type=Path, help="output directory", required=True
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
    output_dir = args.output
    # output_dir = Path("../../data/ref_works_by_year")
    # year=args.year
    # year=2007
    for year in range(2007, 2011):
        df = pd.read_parquet(f"../../data/by_year/t10064_{year}.parquet")
        df = df[df.language == 'en']
        
        out_dir = output_dir / str(year)
        out_dir.mkdir(exist_ok=True)

        # For each paper in that year for a given topic
        for i,row in tqdm(df.iloc[1431:,:].iterrows(), total=len(df.iloc[1431:,:])):
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

            with open(out_dir / f"{row.id.split('/')[-1]}.json", "w") as f:
                json.dump(out, f)


if __name__ == "__main__":
    main()
