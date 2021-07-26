# qc-lookup

This repository contains the parameter and value csv tables needed as input to the OOI QARTOD test algorithms.

Additionally, the current directory contains older qc test tables under the ```qc-lookup``` parent directory. While these are still in use, they are to be deprecated in the future as we roll-out updated QARTOD QC tests.

---
## Directory structure
The structure of this directory utilizes the following pattern:

```
qc-lookup
├── qartod
|   ├── <instrument-class> (e.g. ctdbp)
|   |   ├── climatology_tables
|   |   |   └── <reference designator>_<parameter>.csv
|   |   ├── <instrument-class>_qartod_climatology_test_values.csv
|   |   └── <instrument-class>_qartod_gross_range_test_values.csv
|   └── ...
├── tests (deprecated)
├── data_qc_..._values.csv (In use - to be deprecated)
├── .travis.yml (To be deprecated)
└── README.md

```

For example, this is the directory for the CTDBP instrument class structure:
```
qc-lookup
├── qartod
|   ├── ctdbp
|   |   ├── climatology_tables
|   |   |   ├── CE01ISSM-MFD37-03-CTDBPC000-sea_water_practical_salinity.csv
|   |   |   ├── ...
|   |   |   └── GS01SUMO-RII-02-CTDBPP033-practical_salinity.csv
|   |   ├── ctdbp_qartod_climatology_test_values.csv
|   |   └── ctdbp_qartod_gross_range_test_values.csv
├── ...
```
---
## Methodology

### Gross Range Test
The Gross Range test aims to identify data that fall outside either the sensor measurement range or is a statistical outlier. OOI identifies failed/bad data with a threshold value based on vendor documentation, such as calibration range, for a given sensor. We also calculate suspicious/interesting data thresholds as the mean ± 3 standard deviations based on the historical OOI data for the variable at a deployed location. As implemented by OOI, the Gross Range test identifies data that either fall outside of the indentified sensor operational ranges, and is thus “bad”, or data that are statistical outliers based on the historic OOI data for that location.

### Climatology Test
The Climatology Test is a variation on the Gross Range Test, modifying the relevant suspicious/interesting data thresholds for each calendar-month by accounting for seasonal cycles. The OOI time series are short (<8 years) relative to the World Meteorological Organization (WMO) recommended 30-year climatology reference period. To help ensure quality, we calculate seasonal cycles for a given variable using harmonic analysis, a method that is less susceptible to spurious values that can arise either from data gaps, measurement errors or from the presence of real, but anomalous, geophysical conditions in the available record.  First, we group the data by calendar-month (e.g. January, February, …, December) and calculate the average for each month. Then, we fit the monthly-averaged-data with a two-cycle (annual plus semiannual) harmonic model using Ordinary-Least-Squares. This produces a “climatological” fit for each calendar-month.

Next, we calculate the standard deviation for each calendar-month from the grouped observations for the month. The thresholds for suspicious/interesting data are set as the climatological-fit ± 3 standard deviations. Occasionally, data gaps may mean that there are no historical observations for a given calendar-month. In these instances, we linearly interpolate the threshold from the nearest months. For sensors mounted on profiler moorings or vehicles, we first divide the data into subsets using standardized depth bins to account for differences in seasonality and variability at different depths in the water column. The resulting test identifies data that fall outside of typical seasonal variability determined from the historic OOI data for that location.
