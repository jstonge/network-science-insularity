DATA_DIR=./data
DATA_DIR_BY_YEAR=$(DATA_DIR)/by_year
DATA_DIR_REF_WORKS=$(DATA_DIR)/ref_works_by_year


FRAMEWORK_DIR=./docs
DATA_DIR_OBS=$(FRAMEWORK_DIR)/data

SCRIPT_DIR=./src

#####################
#                   #
#       GLOBAL      #
#                   #
#####################

clean:
	rm -rf docs/.observablehq/cache

########################
#                      #
#        NSF DATA      #
#                      #
########################

import:
	python $(SCRIPT_DIR)/import/import.py -t $1 -o $(DATA_DIR_BY_YEAR)

get-ref-works:
	python $(SCRIPT_DIR)/import/referenced_works.py -t $1 -o $(DATA_DIR_REF_WORKS)
	python $(SCRIPT_DIR)/preprocess/inwards.py -t $1 -o $(DATA_DIR_REF_WORKS)

concat:
	python $(SCRIPT_DIR)/clean/nsf_awards.py -t $1 -o $(DATA_DIR_OBS)
