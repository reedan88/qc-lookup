#!/bin/bash

#####################################################################
# Obtain the various ReferenceDesignator values from asset-management
#####################################################################

# set up links to the CSVs in asset-management/deployment
ls ../../asset-management/deployment/*.csv | awk -F"/" '{print "ln -s ../../asset-management/deployment/" $NF " " $NF}' > amdeploy
source amdeploy

# extract the ReferenceDesignator column values from all these CSVs
for i in $(ls *.csv); do
    x=$(head -1 $i | awk -F "," '{for (x = 1; x <= NF; ++x) if ($x == "Reference Designator") print x}')
    awk -F "," '{print $refdes}' refdes=$x $i | grep -v "Reference Designator" > ${i}.refdes
done

# get all the unique ReferenceDesignator values
sort -u *csv.refdes > refdes.txt

# remove all the CSV links
find . -type l -name "*.csv" -exec unlink {} \;

# cleanup temp files
rm *.refdes amdeploy

##################################################################
# Obtain the units, types and parameters from preload-database.sql
##################################################################

# set up a link to preload-database/preload-database.sql
ln -s ../../preload-database/preload_database.sql preload_database.sql

# get the unit values from preload_database.sql
grep "INSERT INTO \"unit\"" preload_database.sql | awk -F"VALUES" '{print $NF}' | awk -F"," '{print substr($2,2,length($2)-4)}' > unit.txt

# get the type values from preload_database.sql
grep "INSERT INTO \"value_encoding\"" preload_database.sql | awk -F"VALUES" '{print $NF}' | awk -F"," '{print substr($1,2) ":" substr($2,2,length($2)-4)}' > type.txt

# get the parameter values from preload_database.sql and drop duplicates by keeping
# the one with the highest type encoding value; this is done by sorting the results
# in descending order # then retaining the 1st entry for the parameter name
# and re-sorting the results into ascending sequence
grep "INSERT INTO \"parameter\"" preload_database.sql | awk -F"VALUES" '{print $NF}' | awk -F"," '{print substr($2,2,length($2)-2) ":" $3}' | sort -ur > parameter_1.txt
x=zzzzzzzzzz
for i in $(cat parameter_1.txt); do y=$(echo $i | cut -d: -f1); z=$(echo $i | cut -d: -f2); if [[ $x != $y ]]; then echo "$y:$z"; fi; x=$y; done | sort > parameter.txt

# clean up temp file
rm parameter_1.txt

#############################################################
# Substitute pipe-separation for comma-separation in the CSVs
#############################################################

sed 's!,!|!g' ../data_qc_global_range_values.csv > data_qc_global_range_values.psv
sed 's!,!|!g' ../data_qc_gradient_test_values.csv > data_qc_gradient_test_values.psv
sed 's!,!|!g' ../data_qc_spike_test_values.csv > data_qc_spike_test_values.psv
sed 's!,!|!g' ../data_qc_stuck_test_values.csv > data_qc_stuck_test_values.psv
sed 's!,!|!g' ../data_qc_trend_test_values.csv > data_qc_trend_test_values.psv

# the "local" CSV has rows that contain commas within the intended fields; they contain square brackets

# convert all commas to pipes on the "local" CSV on the rows that don't use commas within the 4th field
grep -v "\[" ../data_qc_local_range_values.csv | awk -F"," '{for (x = 1; x <= NF; ++x) if (x < NF) {printf "%s",$x "|"} else {print $x} }' > data_qc_local_range_values.psv.1

# convert all commas to pipes on the "local" CSV on the rows that use commas within the 4th field
grep "\[" ../data_qc_local_range_values.csv | awk -F"," '{for (x = 1; x <= NF; ++x) if (x == NF) {print $x} else {if (x > 3 && x < 6) {printf "%s",$x ","} else {printf "%s",$x "|"} } }' > data_qc_local_range_values.psv.2

# concatenate the 2 files into 1
cat data_qc_local_range_values.psv.* > data_qc_local_range_values.psv

# remove the temp files
rm data_qc_local_range_values.psv.*
