from itertools import chain
import pandas as pd
from pyalex import Works, Authors
from time import sleep
from tqdm import tqdm
import requests
from collections import Counter

def main():
    w = Works()["W2056944867"]
    ref_works = w['referenced_works']
    ref_works_details = []
    for work in ref_works:
        ref_works_details.append(Works()[work])
    
    ref_subfields = Counter([w['primary_topic']['subfield']['display_name'] for w in ref_works_details])
    ref_topics = Counter([w['primary_topic']['display_name'] for w in ref_works_details])

    dict(ref_subfields)

if __name__ == "__main__":
    main()
