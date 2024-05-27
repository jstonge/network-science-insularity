DATA_DIR=./data
DATA_DIR_BY_YEAR=$(DATA_DIR)/by_year
DATA_DIR_REF_WORKS=$(DATA_DIR)/ref_works_by_year


FRAMEWORK_DIR=./docs
DATA_DIR_OBS=$(FRAMEWORK_DIR)/data

SCRIPT_DIR=./src

######################
#                    #
#       SCRIPTS      #
#                    #
######################

.PHONY: ref-works-binary clean import get-ref-works concat preprocess

ref-works-binary: 
	python $(SCRIPT_DIR)/import/import.py -t $(topic) -o $(DATA_DIR_BY_YEAR)
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(topic)').glob('*')], axis=0).to_parquet('data/$(topic).parquet')"
	python $(SCRIPT_DIR)/import/binary_ref_works.py -i $(DATA_DIR) -o $(DATA_DIR_OBS)

clean:
	rm -rf docs/.observablehq/cache

import:
	python $(SCRIPT_DIR)/import/import.py -t $(topic) -o $(DATA_DIR_BY_YEAR)
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(topic)').glob('*')], axis=0).to_parquet('data/$(topic).parquet')"

get-ref-works:
	python $(SCRIPT_DIR)/import/referenced_works.py -t $(topic) -o $(DATA_DIR_REF_WORKS)
	python $(SCRIPT_DIR)/preprocess/inwards.py -t $(topic) -o $(DATA_DIR_REF_WORKS)

concat:
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(topic)').glob('*')], axis=0).to_parquet('data/$(topic).parquet')"

preprocess:
	python $(SCRIPT_DIR)/preprocess/preprocess.py -t $(topic) -o $(DATA_DIR_OBS)
