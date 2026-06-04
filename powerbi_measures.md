# This is a file to highlight a selection of the measures that I have created for the dashboard. Each measure will be pre-empted by a short description and contain comments inside the measure to highlight design decisions that I made and why they were necessary.

### Measure #1: `Total bed nights monthly`
This is the primary measure in the dashboard, that quite a few of the other measures reference in one way or another. It correctly calculates the bed nights for each travel destination within a pretty complex filter-context created by slicers on the pages of the dashboard as well as a few included parameters in the data itself, like the month = 13 and month = 99 parameters, but those will be explained in comments inside the measure below.  
```sql
Total bed nights monthly = 

VAR SelectedStartMonth = --Slicer context. Dashboard users can filter data for sub-periods of a given year, if they'd like to.
    CALCULATE(
        MIN('0.1 Calendar'[MonthNo]),
        FILTER('0.1 Calendar',
            '0.1 Calendar'[Month] = SELECTEDVALUE('0.3 Start_month_table'[Month])
        )
    )

VAR SelectedEndMonth = --Slicer context. Dashboard users can filter data for sub-periods of a given year, if they'd like to.
    CALCULATE(
        MIN('0.1 Calendar'[MonthNo]),
        FILTER('0.1 Calendar',
            '0.1 Calendar'[Month] = SELECTEDVALUE('0.4 End_month_table'[Month])
        )
    )

VAR SelectedYear = MIN('0.1 Calendar'[Year]) --Slicer context. Lets users choose what year to show data for. Other measures include a second slicer context that controls what year to compare data to, like if someone wants to see growth metrics for 2025 compared to 2024, for instance.

VAR chosenDefinition = SELECTEDVALUE('Monthly_data'[Definition_expanded]) --Slicer context. This is called "definition" in the dataset, but in reality it's just a toggle between showing bed nights and arrivals in the context of this dashboard.

VAR SelectedThreshold = SELECTEDVALUE('Bednights Threshold Table'[Filter Value]) --Slicer context. This and the VAR below lets users filter out cities based on their absolute number of bed nights, like choosing to only see destinations with 10M+ bed nights.

VAR BedNightsThreshold = LOOKUPVALUE(
    'Bednights Threshold Table'[Sort Order],
    'Bednights Threshold Table'[Filter Value],
    SelectedThreshold
)

VAR return_value =
    SUMX(
        VALUES('Monthly_data'[Destination]), --The filter context and a few other parameters have to be evaluated on a destination basis. This just makes the measure "loop" through each unique destination and evaluates the context and filters for each destination.
        VAR currentDestination = 'Monthly_data'[Destination]
        VAR HasEndMonth = --The data has been filtered in Python to insure continuity, meaning if a destination has data for a chosen end month of a period, it will have data from January to that end month. Therefore, it's only necessary to check if data for the end month exists for the destination.
            IF(
                SelectedEndMonth = 12, --The dataset primarily consists of monthly data, but does include yearly estimates for some destinations. These should only be shown IF the month period chosen ends in December.
                OR(
                    CALCULATE(
                        COUNTROWS('Monthly_data'),
                        'Monthly_data'[Month] = SelectedEndMonth,
                        'Monthly_data'[Definition_expanded] = chosenDefinition,
                        'Monthly_data'[Destination] = currentDestination,
                        'Monthly_data'[Year] = SelectedYear,
                        'Monthly_data'[Month] <> 99 --The Python code checks if a destination has valid data for each season (fall, winter etc.) for each year. If they have data for all seasons, that means they have valid data for the full year as well. Month = 99 needs to be filtered out here, but it exists, because it's useful in another measure. Further explanation in the measure where it's used (below).
                    ) > 0,
                    CALCULATE(
                        COUNTROWS('Monthly_data'),
                        'Monthly_data'[Month] = 13, --Month = 13 denotes that the data is a yearly estimate, rather than monthly data.
                        'Monthly_data'[Definition_expanded] = chosenDefinition,
                        'Monthly_data'[Destination] = currentDestination,
                        'Monthly_data'[Year] = SelectedYear,
                        'Monthly_data'[Month] <> 99
                    ) > 0
                ),
                CALCULATE( --Destinations with only yearly estimates automatically get filtered out if the end month isn't December since they won't have a row of data with any other month value, so there's no need for a dual-check here, like there is above.
                    COUNTROWS('Monthly_data'),
                    'Monthly_data'[Month] = SelectedEndMonth,
                    'Monthly_data'[Definition_expanded] = chosenDefinition,
                    'Monthly_data'[Destination] = currentDestination,
                    'Monthly_data'[Year] = SelectedYear,
                    'Monthly_data'[Month] <> 99
                ) > 0
            )
        RETURN
            IF(
                NOT HasEndMonth, --If a destination does not have valid data for the selected timeperiod, don't return anything.
                BLANK(),
                IF(
                    SelectedStartMonth = 1 && SelectedEndMonth = 12,
                    CALCULATE(
                        SUM('Monthly_data'[Bed nights]),
                        FILTER('Monthly_data',
                            'Monthly_data'[Definition_expanded] = chosenDefinition &&
                            'Monthly_data'[Destination] = currentDestination &&
                            'Monthly_data'[Year] = SelectedYear &&
                            'Monthly_data'[Month] <> 99
                        )
                    ),
                    CALCULATE(
                        SUM('Monthly_data'[Bed nights]),
                        FILTER('0.1 Calendar',
                            '0.1 Calendar'[MonthNo] >= SelectedStartMonth && 
                            '0.1 Calendar'[MonthNo] <= SelectedEndMonth
                        ),
                        FILTER('Monthly_data', --Don't include destinations that only have yearly estimates, if the specified timeperiod isn't January to December.
                            'Monthly_data'[Definition_expanded] = chosenDefinition &&
                            'Monthly_data'[Destination] = currentDestination &&
                            'Monthly_data'[Month] <> 13 &&
                            'Monthly_data'[Year] = SelectedYear &&
                            'Monthly_data'[Month] <> 99
                        )
                    )
                )
            )
    )

RETURN
    IF(
        BedNightsThreshold = 0,
        return_value,
        IF(
            return_value >= BedNightsThreshold, --Slicer context. This references the same slicer mentioned in the beginning that allows users to filter destinations by their absolute amount of bed nights or arrivals. If a filter is chosen, don't return values for destinations with less bed nights or arrivals than the chosen level.
            return_value,
            BLANK()
        )
    )
```

### Measure #2: [NAME]
[DESCRIPTION goes here]
```sql
Measure code goes here.
```

### Measure #3: [NAME]
[DESCRIPTION goes here]
```sql
Measure code goes here.
```

### Measure #4: [NAME]
[DESCRIPTION goes here]
```sql
Measure code goes here.
```