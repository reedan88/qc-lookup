#!/bin/bash

# Set up links to the CSVs in asset-management/deployment
ls ../../asset-management/deployment/*.csv | awk -F"/" '{print "ln -s ../../asset-management/deployment/" $NF " " $NF}' > amdeploy
source amdeploy
rm amdeploy

# Set up a link to preload-database/preload-database.sql
ln -s ../../preload-database/preload_database.sql preload_database.sql
