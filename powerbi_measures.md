# This is a file to highlight a selection of the measures that I have created for the dashboard. Each measure will be pre-empted by a short description and contain comments inside the measure to highlight design decisions that I made and why they were necessary.

## Measure #1: `Total bed nights monthly`
This is the primary measure in the dashboard, that quite a few of the other measures reference in one way or another. It correctly calculates the bed nights for each travel destination within a pretty complex filter-context created by slicers on the pages of the dashboard as well as a few included parameters in the data itself, like the month = 13 and month = 99 parameters, but those will be explained in comments inside the measure below.  
```sql
Total bed nights monthly = 

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

VAR SelectedThreshold = SELECTEDVALUE('Bednights Threshold Table'[Filter Value])

VAR BedNightsThreshold = LOOKUPVALUE(
    'Bednights Threshold Table'[Sort Order],
    'Bednights Threshold Table'[Filter Value],
    SelectedThreshold
)

VAR return_value =
    SUMX(
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
                        'Monthly_data'[Year] = SelectedYear,
                        'Monthly_data'[Month] <> 99
                    ) > 0,
                    CALCULATE(
                        COUNTROWS('Monthly_data'),
                        'Monthly_data'[Month] = 13,
                        'Monthly_data'[Definition_expanded] = chosenDefinition,
                        'Monthly_data'[Destination] = currentDestination,
                        'Monthly_data'[Year] = SelectedYear,
                        'Monthly_data'[Month] <> 99
                    ) > 0
                ),
                CALCULATE(
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
                NOT HasEndMonth,
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
                        FILTER('Monthly_data',
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
            return_value >= BedNightsThreshold,
            return_value,
            BLANK()
        )
    )
```

## Measure #2: [NAME]
[DESCRIPTION goes here]
```sql
Measure code goes here.
```

## Measure #3: [NAME]
[DESCRIPTION goes here]
```sql
Measure code goes here.
```

## Measure #4: [NAME]
[DESCRIPTION goes here]
```sql
Measure code goes here.
```