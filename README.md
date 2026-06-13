# Transforming tourism data to an interactive dashboard

### Project goal
Since my professional project are mostly confidential and my master's degree doesn't explicitly highlight my python, cloud pipeline and DAX / PowerBi skills, I wanted to create this project to show that I can create a full data pipeline from A-Z. This project does the following:

**Pulls tourism data on bed nights and arrivals for 135+ European destinations from the TourMIS database for the years 2017 to 2025 and uploads it to two BigQuery tables**
The data is mostly on a monthly basis, but some destinations only have yearly data available and this is handled by a combination of Python and DAX code to make sure that data for destinations that only have yearly data available show up when contextually sensible (when the time period selected is January to December for a given year).

The raw dataset is quite messy, in the sense that data is mostly uploaded at the discretion of each destination, meaning there's no guarantee that all destinations have continous data available nor that their data is up-to-date. This is accounted for in the python code, specifically the [format_data_and_calculate_metrics.py](https://github.com/Cazuchi/Transforming-TourMIS-data-into-a-performance-dashboard/blob/main/format_data_and_calculate_metrics.py) script. Destinations are allowed to not have up-to-date data, but it is strictly enforced that any data series included is continous because the dashboard specifically allows for the comparison of user-specified timeperiods to previous periods and non-continuous data would make that functionality useless.  

The code is split up into individual modules with function definitions for each type of functionality (downloading data, authentication, cleanup & formatting etc.) and a main.py script that imports and runs those functions. Each function has a docstring explaining what it does as well as typehints for inputs and outputs of the function. Each module has a module docstring explaining the functionalitty of that module. All code has comments throughout explaining design decisions and non-obvious optimizations.  

The authentication moduls references a local .json file for API credentials, but the cloud version of this script utilizes credentials stored in Google Secret Manager, with a Service Account with permissions specifically scoped to that secret and the relevant BigQuery dataset and tables.  

**Displays the data in an interactive PowerBi dashboard**
While the Python code does a lot of the heavy lifting, there is a lot of filtercontext and data correctness checks that are required in the measures used in the dashboard. Most pages have 6-7-8 slicers for users to use to filter the data which the measures have to account for correctly, making them somewhat long, but I have included a [power_measures.md](https://github.com/Cazuchi/Transforming-TourMIS-data-into-a-performance-dashboard/blob/main/powerbi_measures.md) file to showcase the more interesting measures from the dashboard and explain the design decisions behind the measures.  

The dashboard does not follow a traditional snowflake pattern, primarily because the two fact tables (one for bed nights/arrivals and one for population figures) have drastically different granularity levels. Instead the main fact table with bed nights and arrivals data is connected to a calendar table, while all other tables are designed as standalone parameter / dimension tables and measures reference the filtercontext of the page through SELECTEDVALUE() statements and appropriate logic to handle the user-specified context.  

### The dashboard is available here:
https://app.powerbi.com/view?r=eyJrIjoiOGM4Yjk3NGUtMmVlNS00NTEyLTk3MjUtNWNiNDQ4ZDg2NTdhIiwidCI6IjcwZjRhY2NiLTM3N2UtNDg5ZS04YjhiLTI4NjllYjQwYmQ3MSJ9

### Skills used in this project:
* Python
* DAX / PowerBi
* Google Compute Engine / Secret Manager / IAM / BigQuery

### Data source
This project pulls bed nights and arrivals data from an Austrian University databash with aggregated data from multiple national statistics bureaus databases. So the data itself is publicly available, but I have permission to use this aggregated dataset in this project, which requires you to request a TourMIS account, if you would like to use the same data.