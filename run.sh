#!/bin/bash

set -e
DATA_PATH=./data
DOWNLOAD_PATH=$DATA_PATH/download
OUTPUT_PATH=$DATA_PATH/output
LOG_PATH=$DATA_PATH/log

function run_spider() {
	spider=$1
	output=$2

	mkdir -p $DOWNLOAD_PATH $OUTPUT_PATH $LOG_PATH
	time scrapy runspider \
		--loglevel=INFO \
		--logfile=$LOG_PATH/"$spider".log \
		-s HTTPCACHE_ENABLED=true \
		-s HTTPCACHE_IGNORE_HTTP_CODES=400,401,402,403,404,500,501,502 \
		-s AUTOTHROTTLE_ENABLED=true \
		-o $output \
		src/spiders/"$spider".py
}

run_spider tce_list_files $OUTPUT_PATH/tce-link.csv
run_spider tce_download_files $OUTPUT_PATH/tce-download.csv
run_spider crmpr_doctors $OUTPUT_PATH/crmpr-doctor.csv
