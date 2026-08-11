# Share of children in primary school age who are in school - Data package

This data package contains the data that powers the chart ["Share of children in primary school age who are in school"](https://ourworldindata.org/grapher/primary-enrollment-selected-countries?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website. It was downloaded on August 11, 2026.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For most countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Net enrollment rate in primary education
The share of children of [primary](#dod:primary-education) school age (typically 6–11 years) who are enrolled in primary education.
Last updated: May 12, 2026  
Next update: May 2027  
Date range: 1820–2025  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
UNESCO Institute for Statistics (2026); Lee and Lee (2016) – with minor processing by Our World in Data

#### Full citation
UNESCO Institute for Statistics (2026); Lee and Lee (2016) – with minor processing by Our World in Data. “Net enrollment rate in primary education” [dataset]. UNESCO Institute for Statistics, “UNESCO Institute for Statistics (UIS) - Education”; Lee and Lee, “Human Capital in the Long Run” [original data].
Source: UNESCO Institute for Statistics (2026), Lee and Lee (2016) – with minor processing by Our World In Data

### What you should know about this data
- This indicator combines data from two sources. Where UNESCO administrative records are available (from as early as the 1970s for some countries), those are used. Before 1985, where UNESCO data is not available, it draws on adjusted enrollment ratios from [Lee and Lee (2016)](https://barrolee.github.io/BarroLeeDataSet/DataLeeLee.html) — modified gross enrollment ratios that account for grade repetition, serving as the best available approximation of net enrollment rates for periods when age-specific enrollment data were not widely collected.
- The net enrollment rate shows what share of children are enrolled at the education level intended for their age — for example, a rate of 90% means 90% of children in the official age group are enrolled at that level.
- A rate below 100% doesn't necessarily mean those children are out of school — some may be enrolled at a different level than expected for their age.

### Sources

#### UNESCO Institute for Statistics – UNESCO Institute for Statistics (UIS) - Education
Retrieved on: 2026-05-12  
Retrieved from: https://databrowser.uis.unesco.org/resources/bulk  

#### Lee and Lee – Human Capital in the Long Run
Retrieved on: 2023-11-20  
Retrieved from: https://barrolee.github.io/BarroLeeDataSet/DataLeeLee.html  

#### Notes on our processing step for this indicator
- UNESCO OPRI data (based on school censuses that track enrollment by individual age) is used wherever available. Before 1985, for country-years without UNESCO coverage, data comes from [Lee and Lee (2016)](https://barrolee.github.io/BarroLeeDataSet/DataLeeLee.html), whose enrollment ratios adjust for grade repetition, bringing them closer to a true net enrollment rate than raw gross enrollment ratios.


    