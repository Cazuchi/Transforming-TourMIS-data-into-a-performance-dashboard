# This is a file to highlight a selection of the measures that I have created for the dashboard. Each measure will be pre-empted by a short description and contain comments inside the measure to highlight design decisions that I made and why they were necessary.

### Measure #1: `Total bed nights monthly`
This is the primary measure in the dashboard, that quite a few of the other measures reference in one way or another. It correctly calculates the bed nights for each travel destination within a pretty complex filter-context created by slicers on the pages of the dashboard as well as a few included parameters in the data itself, like the month = 13 and month = 99 parameters, but those will be explained in comments inside the measure below.  

Because this measure is intended to be useable for showing both total bed nights across all destinations and bed nights for individual destinations, the "loop" to evaluate the context for each destination is required. As opposed to if this was meant for use solely in visualizations that only show the result on a per destination basis.
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

### Measure #2: `Median percentage growth`
A modified version of measure #1. Calculates the median growth rate amongst all destinations with valid data and returns it for use in a dynamic label. This can technically also be used to return the individual growth rates for each destination, but the measure is way overkill for that usecase. The graph in the dashboard that shows growth rates per city uses a simple measure that calculates the growth rate per city by dividing the measure for bed nights in the main selected timeperiod and the measure for bed nights in the comparison timeperiod.

Because this measure is intended to be useable for showing the median growth across all destinations, the "loop" to evaluate the context for each destination is required. As opposed to if this was meant for use solely in visualizations that only show the result on a per destination basis.
```sql
Median percentage growth = 

VAR SelectedStartMonth = 
    CALCULATE(
        MIN('0.1 Calendar'[MonthNo]),
        FILTER('0.1 Calendar',
            '0.1 Calendar'[Month] = SELECTEDVALUE('0.3 Start_month_table'[Month])
        )
    )

VAR SelectedEndMonth = 
    CALCULATE(
        MIN('0.1 Calendar'[MonthNo]),
        FILTER('0.1 Calendar',
            '0.1 Calendar'[Month] = SELECTEDVALUE('0.4 End_month_table'[Month])
        )
    )

VAR SelectedYear = MIN('0.1 Calendar'[Year])

VAR chosenDefinition = SELECTEDVALUE('Monthly_data'[Definition_expanded])

VAR return_value =
    MEDIANX(
        VALUES('Monthly_data'[Destination]),
        VAR currentDestination = 'Monthly_data'[Destination]
        VAR HasEndMonth =
            IF(
                SelectedEndMonth = 12,
                OR(
                    CALCULATE(
                        COUNTROWS('Monthly_data'),
                        'Monthly_data'[Month] = SelectedEndMonth,
                        'Monthly_data'[Definition_expanded] = chosenDefinition,
                        'Monthly_data'[Destination] = currentDestination,
                        'Monthly_data'[Year] = SelectedYear
                    ) > 0,
                    CALCULATE(
                        COUNTROWS('Monthly_data'),
                        'Monthly_data'[Month] = 13,
                        'Monthly_data'[Definition_expanded] = chosenDefinition,
                        'Monthly_data'[Destination] = currentDestination,
                        'Monthly_data'[Year] = SelectedYear
                    ) > 0
                ),
                CALCULATE(
                    COUNTROWS('Monthly_data'),
                    'Monthly_data'[Month] = SelectedEndMonth,
                    'Monthly_data'[Definition_expanded] = chosenDefinition,
                    'Monthly_data'[Destination] = currentDestination,
                    'Monthly_data'[Year] = SelectedYear
                ) > 0
            )
        RETURN IF(
            HasEndMonth, 
            IF(
                [Total bed nights monthly]/[Total bed nights monthly comp. year] < 50,
                [Total bed nights monthly]/[Total bed nights monthly comp. year] - 1,
                BLANK()
            ),
            BLANK())
    )

RETURN return_value
```

### Measure #3: `Population density`
This measure also uses a lot of the same logic as measure #1, however this measure is only ever used in visualizations that show the result on a per destination basis, so the "loop" over each destination is not necessary.

This measure finds the bed nights / arrivals in a given destination and divides it by the destinations population to get a population density measure. A proxy for the level of tourism in a destination relative to the size of the population. Higher numbers generally mean more pressure on the destination from the tourism activities there.
```sql
Population Density = 

VAR chosenDefinition = SELECTEDVALUE('Monthly_data'[Definition_expanded])
VAR chosenDestination = SELECTEDVALUE('Monthly_data'[Destination])
VAR chosenYear = SELECTEDVALUE('0.1 Calendar'[Year])
VAR chosenSeason = SELECTEDVALUE('Monthly_data'[Season])
Var chosenMarket = SELECTEDVALUE(Monthly_data[Market - Copy])

VAR populationNumber = SUMX(
    FILTER(
        'Population_statistics',
        'Population_statistics'[Definition] = chosenDefinition &&
        'Population_statistics'[Destination] = chosenDestination &&
        'Population_statistics'[Year] = chosenYear
    ),
    'Population_statistics'[Population]
)

VAR bedNights = CALCULATE(
    SUM(
        'Monthly_data'[Bed nights]),
        FILTER(
            'Monthly_data',
            'Monthly_data'[Season] = chosenSeason &&
            'Monthly_data'[Definition_expanded] = chosenDefinition
    )
)

VAR FullYearBedNights = CALCULATE(
    SUM('Monthly_data'[Bed nights]),
    ALL('Monthly_data'),
    'Monthly_data'[Definition_expanded] = chosenDefinition,
    'Monthly_data'[Destination] = chosenDestination,
    'Monthly_data'[Year] = chosenYear,
    'Monthly_data'[Market - Copy] = chosenMarket,
    'Monthly_data'[Month] <> 99
)


VAR SelectedBedNightsThreshold = SELECTEDVALUE('Bednights Threshold Table'[Filter Value])

VAR BedNightsThreshold = LOOKUPVALUE(
    'Bednights Threshold Table'[Sort Order],
    'Bednights Threshold Table'[Filter Value],
    SelectedBedNightsThreshold
)

VAR PopulationDensity = IF(
    BedNightsThreshold = 0,
    DIVIDE(bedNights, populationNumber),
    IF(
        FullYearBedNights < BedNightsThreshold,
        DIVIDE(bedNights, populationNumber),
        BLANK()
    )
)

VAR selectedThreshold = SELECTEDVALUE('Population Density Threshold Table'[Filter Value]) --Slicer context. There's a slicer that allows users to filter destinations by their population density figure, because some destinations have extreme values that can make it difficult to gauge the level in other destinations in visualizations.
VAR thresholdValue = 
    IF(
        selectedThreshold = "None",
        BLANK(),
        VALUE(SUBSTITUTE(SUBSTITUTE(selectedThreshold, ">", "")," ratio",""))
    )

RETURN
    IF(
        ISBLANK(thresholdValue),
        PopulationDensity,  // No threshold selected
        IF(PopulationDensity > thresholdValue, BLANK(), PopulationDensity)  // Zero out values above threshold
    )
```

### Measure #4: `Top destinations dynamic text box`
Just a dynamic label that changes based on the user's choices for the slicers on the page. Mostly just references existing measures and the user's selected values in the slicers on the page.
```sql
Top destinations dynamic text box = 

VAR bednights_or_arrivals = IF(SELECTEDVALUE(Monthly_data[Definition_expanded]) = "Bednights - preferred definition", "bednights", "arrivals")

VAR dynamic_text = "This view shows the top 20 travel destinations based on total " &
bednights_or_arrivals &
" from " &
SELECTEDVALUE('0.3 Start_month_table'[Month]) &
" to " &
SELECTEDVALUE('0.4 End_month_table'[Month]) &
" " &
MIN('0.1 Calendar'[Year]) &
", as well as the top 20 travel destinations based on percentage growth of " &
bednights_or_arrivals &
" compared to " & 
MIN('0.2 Comparison calendar'[Year]) &
" in the same months." &
UNICHAR(10) &
UNICHAR(10) &
"For context, a total of " &
[City counter] &
" travel destinations have valid data for this filter context, with a median percentage growth of " &
FORMAT([Median percentage growth], "0.0%") &
"." &
UNICHAR(10) &
UNICHAR(10) &
"Other filters may have been applied. Open the filters menu to see the full filter context for the displayed data."

RETURN dynamic_text
```