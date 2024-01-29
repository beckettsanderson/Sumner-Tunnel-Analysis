# -*- coding: utf-8 -*-
"""
@author: Beckett Sanderson
@date: 7.24.23

Analysis on the Sumner Tunnel closure with a focus on the ridership before
and after the closure for each line on both the overall transit line level
and specific stop level
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

pd.options.display.max_columns = 50
pd.options.display.max_rows = 1500
pd.options.mode.chained_assignment = None  # default='warn'

BLUE = "C:/Users/bSANDERSON/Box/Projects/Agency-wide/Sumner Tunnel Dashboard/Data Samples/Triverus_Exports/Blue_Line_Sumner.csv"
ORANGE = "C:/Users/bSANDERSON/Box/Projects/Agency-wide/Sumner Tunnel Dashboard/Data Samples/Triverus_Exports/Orange_Line_Sumner.csv"

# set dates for before and after the Sumner Tunnel closure
BC_SUMNER = list(pd.date_range(dt.datetime(2023, 6, 1),
                               dt.datetime(2023, 7, 4),
                               freq='D'))
AC_SUMNER = list(pd.date_range(dt.datetime(2023, 7, 5),
                               dt.datetime(2023, 9, 1),
                               freq='D'))

# set of stations north of State Street for Orange Line
OL_STATIONS = ['Oak Grove', 'Malden Center', 'Wellington', 'Assembly',
               'Sullivan Square', 'Community College', 'North Station',
               'Haymarket', 'State Street']
BL_STATIONS = ['Wonderland', 'Revere Beach', 'Beachmont', 'Suffolk Downs',
               'Orient Heights', 'Wood Island', 'Airport', 'Maverick',
               'Aquarium', 'State Street', 'Government Center', 'Bowdoin']


def get_line_entries(df, line, weekdays_only=False):
    """
    Clean up line data and adjusts it based on the necessary stops and requests

    Parameters
    ----------
    df : DataFrame
        df containing orange line stop data.
    line : Str
        string of the transit line to clean. set up for orange and blue.

    Returns
    -------
    cleaned_df : DataFrame
        the cleaned data for the orange line.

    """
    if line == 'Blue Line':
        stops = ['Government Center', 'State Street']
    elif line == 'Orange Line':
        stops = ['Haymarket', 'North Station', 'State Street']
        df = df.loc[(df['Stop Name'].isin(OL_STATIONS))]
    else:
        print('\nNo stops set for this station. Please try again.\n')

    # assign stops to the line
    df.loc[(df['Stop Name'].isin(stops)),
           'Route Or Line'] = line

    # set the service dates to datetime
    df['Service Date'] = pd.to_datetime(df['Service Date'])

    # check if only weekdays are needed
    if weekdays_only:

        # select only weekdays
        df = df.loc[(df['day'] == 'Weekday')]

    # get only the selected line's data
    cleaned_df = df.loc[df['Route Or Line'] == line]

    return cleaned_df


def daily_ridership(df):
    """
    Groups the data by date and gets the total ridership for that date for
    each stop on the line

    Parameters
    ----------
    df : DataFrame
        df containing ridership data for the set.

    Returns
    -------
    grouped_df: DataFrame
        df grouped by date and stop with the total ridership for that date

    """
    # split by day and sum both valid and fradulent entries
    grouped_df = df.groupby(['Service Date', 'Stop Name'],
                            as_index=False)['Total Entries'].agg('sum').round()
    grouped_df['Total Entries'] = grouped_df['Total Entries'].astype(int)

    return grouped_df


def plot_ridership(df_lst, line_lst, title_addition=''):
    """
    Plot the ridership for an input transit line or set of lines with the
    ridership per day plotted before and after the sumner tunnel closure

    Parameters
    ----------
    df_lst : lst
        list of dataframes.
    line_lst : lst
        corresponding list of transit lines to the dataframes.
    title_addition : str, optional
        any additional information to add onto the title. The default is ''.

    Returns
    -------
    None.

    """
    # create a dict of the lines and their respective df
    line_dict = dict(zip(line_lst, df_lst))

    # loop through each line and graph it on the chart
    for line in line_dict:

        # sort to only be grouped by day
        daily_rides = line_dict[line].groupby(['Service Date'],
                                              as_index=False).sum(numeric_only=True)

        # plot a line plot of the ridership over time
        plt.plot(daily_rides['Service Date'],
                 daily_rides['Total Entries'],
                 marker=".",
                 color=line.split()[0],
                 label=line)

    # adjust x-axis spacing
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gcf().autofmt_xdate()

    # add line and shading at sumner tunnel closure
    plt.axvline(dt.datetime(2023, 7, 4),
                linestyle='--',
                linewidth=2,
                color='black',
                label='Sumner Tunnel Closure')
    plt.gca().axvspan(dt.datetime(2023, 6, 1),
                      dt.datetime(2023, 7, 4),
                      alpha=0.6,
                      color='lightgrey')

    # graph organization
    plt.title('Ridership During Sumner Tunnel Closure' + title_addition)
    plt.xlabel('Date')
    plt.ylabel('Ridership per Day')
    plt.gca().legend(loc='upper center',
                     bbox_to_anchor=(0.5, -0.30),
                     fancybox=True,
                     ncol=3)

    plt.show()


def overall_stats(df, line):
    """
    Calculate overall ridership stats on an overall line scale to show the
    most recent day's ridership, ridership before the closing of the tunnel,
    and the percentage change between the two

    Parameters
    ----------
    df : DataFrame
        df with the data for the line.
    line : str
        string of the transit line the data is for.

    Returns
    -------
    None.

    """
    # sort to only be grouped by day
    daily = df.groupby(['Service Date'], as_index=False).sum(numeric_only=True)

    # get the most recent day of data's ridership
    updated_day = daily['Service Date'].max()
    updated_num = daily.loc[(daily['Service Date'] == updated_day)]['Total Entries'].values[0]
    print(f'\n{line} total ridership on most recent day, {updated_day.strftime("%d %b %Y")}: {updated_num}')

    # get average ridership before sumner closing
    before_sumner = daily.loc[(daily['Service Date'].isin(BC_SUMNER))]
    avg_ride_bc = int(round(before_sumner['Total Entries'].mean()))
    print(f'{line} average ridership before closing Sumner Tunnel: {avg_ride_bc}')

    # calculate the percentage change in ridership to most recent num
    delta = int((((updated_num - avg_ride_bc) / avg_ride_bc) * 100).round())
    print(f'{line} percent change in ridership after Sumner Tunnel closing: {delta}%\n')

    print('--------------------------------------------------------')


def check_missing(after_sumner, line):
    """
    Check the data for any stations missing data on any of the days in the
    dataset and display which ones are missing on which days

    Parameters
    ----------
    after_sumner : DataFrame
        df with the station level data of ridership after the sumner closure.
    line : str
        the name of the transit line to analyze.

    Returns
    -------
    None.

    """
    # get counts for each day and see stations lower than 12 (num stations)
    date_counts = after_sumner['Service Date'].value_counts()

    if line.startswith('Orange Line'):
        dates_missing = list(date_counts[date_counts < len(OL_STATIONS)].index)
    elif line.startswith('Blue Line'):
        dates_missing = list(date_counts[date_counts < len(BL_STATIONS)].index)
    else:
        dates_missing = []

    # for each date check which stations are missing
    for date in dates_missing:

        # create a list of each of the stops missing from that date
        cur_date_df = after_sumner.loc[(after_sumner['Service Date'] == date)]
        temp_stops = cur_date_df['Stop Name'].tolist()

        # display the stops that are missing data
        if line.startswith('Orange Line'):
            print(f"Missing values for {line} on {date.strftime('%d %b %Y')}: {(set(OL_STATIONS).difference(temp_stops))}\n")
        elif line.startswith('Blue Line'):
            print(f"Missing values for {line} on {date.strftime('%d %b %Y')}: {(set(BL_STATIONS).difference(temp_stops))}\n")

    # # get num of missing values for each station
    # station_counts = after_sumner['Stop Name'].value_counts()

    # return station_counts


def station_stats(df, line):
    """
    Calculate ridership stats on the station level to show average ridership
    before and after the sumner tunnel closure as well as the differential
    and percentage change between those periods

    Parameters
    ----------
    df : DataFrame
        df with the data for the line.
    line : str
        string of the transit line the data is for.

    Returns
    -------
    None.

    """
    # select only dates before and after closing into separate dataframes
    before_sumner = df.loc[(df['Service Date'].isin(BC_SUMNER))]
    after_sumner = df.loc[(df['Service Date'].isin(AC_SUMNER))]

    # get the station counts for all the stops on the line
    check_missing(after_sumner, line)

    # get dates for labels
    bc_first_date = before_sumner['Service Date'].min().strftime("%d %b %Y")
    bc_last_date = before_sumner['Service Date'].max().strftime("%d %b %Y")
    ac_first_date = after_sumner['Service Date'].min().strftime("%d %b %Y")
    ac_last_date = after_sumner['Service Date'].max().strftime("%d %b %Y")

    # group by stations to get data for before and after closure
    bc_stations = before_sumner.groupby(["Stop Name"])["Total Entries"].mean()
    ac_stations = after_sumner.groupby(["Stop Name"])["Total Entries"].mean()

    # add each of the before and after stats into a dataframe
    full_df = pd.concat([bc_stations, ac_stations],
                        axis=1,
                        keys=['BC', 'AC'])

    # properly format the average ridership and add a total column
    full_df['BC'] = full_df['BC'].apply(lambda x: int(round(x)))
    full_df['AC'] = full_df['AC'].apply(lambda x: int(round(x)))
    line_name = line.split()[0].upper() + " " + line.split()[1].upper()
    full_df.loc[line_name + ' TOTAL'] = full_df.sum(numeric_only=True)

    # calulate difference and percent change into different columns
    full_df['Differential'] = full_df['AC'] - full_df['BC']
    full_df['% Change'] = round(((full_df['AC'] - full_df['BC']) / full_df['BC']) * 100)
    full_df['% Change'] = full_df['% Change'].astype(int).astype(str)
    full_df['% Change'] = full_df['% Change'].apply(lambda x: x + "%")

    # adjust names and order based on order of stations
    full_df.columns = ['Before Closing', 'After Closing', 'Differential',
                        '% Change']
    if line.startswith('Orange Line'):
        full_df = full_df.reindex(OL_STATIONS + ['ORANGE LINE TOTAL'])
    elif line.startswith('Blue Line'):
        full_df = full_df.reindex(BL_STATIONS + ['BLUE LINE TOTAL'])

    # display the results
    print(f'AVG RIDERSHIP BEFORE AND AFTER SUMNER TUNNEL CLOSING FOR {line.upper()}\n')
    print(f'Dates included before closing: \t{bc_first_date} - {bc_last_date}')
    print(f'Dates included after closing: \t{ac_first_date} - {ac_last_date}\n')
    print(full_df)

    print('\n--------------------------------------------------------\n')


def Main():

    # read in the data for both blue and orange lines
    blue_df = pd.read_csv(BLUE)
    orange_df = pd.read_csv(ORANGE)

    # get ol and bl data and assign station data correctly (weekdays only and all)
    ol_cleaned = get_line_entries(orange_df, 'Orange Line')
    bl_cleaned = get_line_entries(blue_df, 'Blue Line')
    ol_weekdays_cleaned = get_line_entries(orange_df,
                                           'Orange Line',
                                           weekdays_only=True)
    bl_weekdays_cleaned = get_line_entries(blue_df,
                                           'Blue Line',
                                           weekdays_only=True)

    # group the lines by date for ridership (weekdays only and all)
    ol_daily = daily_ridership(ol_cleaned)
    bl_daily = daily_ridership(bl_cleaned)
    ol_weekdays_daily = daily_ridership(ol_weekdays_cleaned)
    bl_weekdays_daily = daily_ridership(bl_weekdays_cleaned)

    # plot the lines with their daily ridership for both lines together
    plot_ridership([ol_daily, bl_daily], ['Orange Line', 'Blue Line'])

    # plot the lines with their daily ridership for each individual line
    plot_ridership([ol_daily], ['Orange Line'])
    plot_ridership([bl_daily], ['Blue Line'])

    # plot daily ridership for weekdays only for both lines
    plot_ridership([ol_weekdays_daily, bl_weekdays_daily],
                    ['Orange Line', 'Blue Line'],
                    title_addition=' (Weekdays Only)')

    # plot daily ridership for weekdays only for each individual line
    plot_ridership([ol_weekdays_daily],
                    ['Orange Line'],
                    title_addition=' (Weekdays Only)')
    plot_ridership([bl_weekdays_daily],
                    ['Blue Line'],
                    title_addition=' (Weekdays Only)')

    # get the overall transit line stats for the lines
    overall_stats(ol_daily, 'Orange Line')
    overall_stats(bl_daily, 'Blue Line')
    overall_stats(ol_weekdays_daily, 'Orange Line (weekdays)')
    overall_stats(bl_weekdays_daily, 'Blue Line (weekdays)')

    # get the station specific stats
    station_stats(ol_daily, 'Orange Line')
    station_stats(bl_daily, 'Blue Line')
    station_stats(ol_weekdays_daily, 'Orange Line (weekdays)')
    station_stats(bl_weekdays_daily, 'Blue Line (weekdays)')


Main()
