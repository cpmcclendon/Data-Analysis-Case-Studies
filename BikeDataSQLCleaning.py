## Bike Data
## Collin McClendon
## Data Source: https://divvy-tripdata.s3.amazonaws.com/index.html
## Case Study Updated
import pandas as pd
import csv
import os
import sqlite3

dataset = ["202203-divvy-tripdata.csv", "202204-divvy-tripdata.csv", "202205-divvy-tripdata.csv",
           "202206-divvy-tripdata.csv", "202207-divvy-tripdata.csv", "202208-divvy-tripdata.csv",
           "202209-divvy-tripdata.csv", "202210-divvy-tripdata.csv", "202211-divvy-tripdata.csv",
           "202212-divvy-tripdata.csv", "202301-divvy-tripdata.csv", "202302-divvy-tripdata.csv"]      

for data in dataset: ##Show the first few rows and column datatypes for each csv file.
    read = pd.read_csv(data, delimiter = ",")
    pd.set_option('display.max_columns', None)
    print(f"Data display for {data}")
    print(read.head())
    print(read.dtypes)

##These are the columns for each csv file.
##ride_id             rideable_type       started_at          ended_at
##start_station_name  start_station_id    end_station_name    end_station_id
##start_lat           start_lng           end_lat             end_lng
##member_casual  

with sqlite3.connect("bikedata.db") as connection:
    c = connection.cursor()

    c.execute("""DROP TABLE IF EXISTS divvybikedata""") ##Testing purposes

    c.execute("""CREATE TABLE IF NOT EXISTS divvybikedata(
            ride_id text,
            rideable_type text,
            started_at text,
            ended_at text,
            start_station_name text,
            start_station_id text,
            end_station_name text,
            end_station_id text,
            start_lat real,
            start_lng real,
            end_lat real,
            end_lng real,
            member_casual text 
        )""") ##Set up sqlite columns based on the datatypes.

    for i in dataset: ##Insert each csv file into a Sqlite table.
        contents = csv.reader(open(i))
        next(contents) ##Skips the header row so it does not get included as part of the values.
        c.executemany("INSERT INTO divvybikedata(ride_id, rideable_type, started_at," \
                      "ended_at, start_station_name, start_station_id, end_station_name," \
                      "end_station_id, start_lat, start_lng, end_lat, end_lng," \
                      "member_casual) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", contents)

    rows = c.execute("""SELECT *
                     FROM divvybikedata
                     LIMIT 10""").fetchall()
    for r in rows: ##Print the first 10 rows of the table to see what to work with in sqlite.
        print(r)        

    ##Showing dirty data.

    c.execute("""SELECT COUNT(*) 
              FROM divvybikedata""")
    before = c.fetchone()
    print("Number of rows before cleaning")
    print(before[0]) ##Show the total number of rows before cleaning the data.

    c.execute("""SELECT COUNT(*)
              FROM divvybikedata
              WHERE ((strftime('%s', (ended_at)) - strftime('%s', (started_at))) <= 0)""")
    result = c.fetchone()
    print("Number of rows with the time difference at 0 seconds or less")
    print(result[0]) ##Show the total number of rows with time differece of 0 seconds or less.

    c.execute("""SELECT COUNT(*)
              FROM divvybikedata
              WHERE (start_station_name is NULL) OR (start_station_name = '') OR
              (start_station_id is NULL) OR (start_station_id = '') OR
              (end_station_name is NULL) OR (end_station_name = '') OR
              (end_station_id is NULL) OR (end_station_id = '')""")
    emptystation = c.fetchone()
    print("Number of rows with empty station name and id values")
    print(emptystation[0]) ##Show the total number of rows with empty station names and id values.

    c.execute("""SELECT COUNT(*)
              FROM divvybikedata
              WHERE (start_lat is NULL) OR (start_lat = '') OR
              (start_lng is NULL) OR (start_lng = '') OR
              (end_lat is NULL) OR (end_lat = '') OR
              (end_lng is NULL) OR (end_lng = '')""")
    emptylocation = c.fetchone()
    print("Number of rows with empty latitude and longitude values")
    print(emptylocation[0]) ##Show the total number of rows wiht empty latitude and longitude values.

    c.execute("""SELECT COUNT(*) 
              FROM divvybikedata""")
    alldata = c.fetchone()
    
    c.execute("""SELECT COUNT(*) 
              FROM (SELECT DISTINCT * FROM divvybikedata)""")
    unique = c.fetchone()
    print("Number of duplicated rows")
    print(alldata[0] - unique[0]) ##Show the total number of duplicated rows.
    
    c.execute("""SELECT COUNT(*)
              FROM divvybikedata
              WHERE (((start_lat NOT BETWEEN 40.00 AND 43.00) AND
              (start_lat is NOT NULL AND start_lat != "")) OR
              ((start_lng NOT BETWEEN -89.00 AND -86.00) AND
              (start_lng is NOT NULL AND start_lng != "")) OR
              ((end_lat NOT BETWEEN 40.00 AND 43.00) AND
              (end_lat is NOT NULL AND end_lat != "")) OR
              ((end_lng NOT BETWEEN -89.00 AND -86.00) AND
              (end_lat is NOT NULL AND end_lat != "")))""")
    outside = c.fetchone()
    print("Number of rows with latitude and longitude outside the range")
    print(outside[0]) ##Show the total number of rows with location outside the range (Chicago).

    c.execute("""SELECT COUNT(*)
              FROM divvybikedata
              WHERE LENGTH(ride_id) != LENGTH(trim(ride_id)) OR
              LENGTH(rideable_type) != LENGTH(trim(rideable_type)) OR
              LENGTH(started_at) != LENGTH(trim(started_at)) OR
              LENGTH(ended_at) != LENGTH(trim(ended_at)) OR
              LENGTH(start_station_name) != LENGTH(trim(start_station_name)) OR
              LENGTH(start_station_id) != LENGTH(trim(start_station_id)) OR
              LENGTH(end_station_name) != LENGTH(trim(end_station_name)) OR
              LENGTH(end_station_id) != LENGTH(trim(end_station_id)) OR
              LENGTH(member_casual) != LENGTH(trim(member_casual))""")
    trail = c.fetchone()
    print("Number of rows with trailing spaces in text values")
    print(trail[0]) ##Show the total number of rows with any trailing spaces.

    ##Deleting and Cleaning rows.

    c.execute("""DELETE 
              FROM divvybikedata
              WHERE ((strftime('%s', (ended_at)) - strftime('%s', (started_at))) <= 0)""")
    print("Deleted rows with a time difference of 0 seconds or less.")
    
    c.execute("""DELETE
              FROM divvybikedata
              WHERE (start_station_name is NULL) OR (start_station_name = '') OR
              (start_station_id is NULL) OR (start_station_id = '') OR
              (end_station_name is NULL) OR (end_station_name = '') OR
              (end_station_id is NULL) OR (end_station_id = '')""")
    print("Deleted rows with empty station names and id values.")
    
    c.execute("""DELETE
              FROM divvybikedata
              WHERE (start_lat is NULL) OR (start_lat = '') OR
              (start_lng is NULL) OR (start_lng = '') OR
              (end_lat is NULL) OR (end_lat = '') OR
              (end_lng is NULL) OR (end_lng = '')""")
    print("Deleted rows with empty latitude and longitude values.")

    c.execute("""DELETE
              FROM divvybikedata
              WHERE (((start_lat NOT BETWEEN 40.00 AND 43.00) AND
              (start_lat is NOT NULL AND start_lat != "")) OR
              ((start_lng NOT BETWEEN -89.00 AND -86.00) AND
              (start_lng is NOT NULL AND start_lng != "")) OR
              ((end_lat NOT BETWEEN 40.00 AND 43.00) AND
              (end_lat is NOT NULL AND end_lat != "")) OR
              ((end_lng NOT BETWEEN -89.00 AND -86.00) AND
              (end_lat is NOT NULL AND end_lat != "")))""")
    print("Deleted rows with location outside the range (Chicago).")

    c.execute("""UPDATE divvybikedata
              SET ride_id = trim(ride_id),
              rideable_type = trim(rideable_type),
              started_at = trim(started_at),
              ended_at = trim(ended_at),
              start_station_name = trim(start_station_name),
              start_station_id = trim(start_station_id),
              end_station_name = trim(end_station_name),
              end_station_id = trim(end_station_id),
              member_casual = trim(member_casual)""")
    print("Cleaned up trailing spaces in the values.")

    ##Showing cleaned up data.
    
    c.execute("""SELECT COUNT(*) 
              FROM divvybikedata""")
    after = c.fetchone()
    print("Number of rows after cleaning")
    print(after[0]) ##Show the total number of rows after cleaning the data.


    ##Adding a few calculations to the table.

    c.execute("""ALTER TABLE divvybikedata
            ADD COLUMN time_hours real
            GENERATED ALWAYS AS
            ((JulianDay(ended_at) - JulianDay(started_at)) * 24)
            """)

    c.execute("""ALTER TABLE divvybikedata
            ADD COLUMN year_month text
            GENERATED ALWAYS AS
            (strftime('%Y-%m', started_at))
            """)

    c.execute("""ALTER TABLE divvybikedata
            ADD COLUMN day_of_week text
            GENERATED ALWAYS AS
            (CASE (strftime('%w', started_at))
                WHEN '0' THEN 'Sunday'
                WHEN '1' THEN 'Monday'
                WHEN '2' THEN 'Tuesday'
                WHEN '3' THEN 'Wednesday'
                WHEN '4' THEN 'Thursday'
                WHEN '5' THEN 'Friday'
                ELSE 'Saturday'
                END)
            """)

    ##Rows to remove for easier analysis:
    ##started_at          ended_at            start_station_id  end_station_id
    ##start_lat           start_lng           end_lat             end_lng
    
    rows = c.execute("""SELECT *
                     FROM divvybikedata LIMIT 10""").fetchall()
    print(rows)

    altered_data = c.execute("""SELECT ride_id, rideable_type, start_station_name, end_station_name, member_casual, time_hours, year_month, day_of_week
                    FROM divvybikedata""").fetchall()

    c.execute("""DROP TABLE IF EXISTS divvybikedata""")

    c.execute("""CREATE TABLE IF NOT EXISTS divvybikedata ( 
                    ride_id text,
                    rideable_type text,
                    start_station_name text,
                    end_station_name text,
                    member_casual text,
                    time_hours real,
                    year_month text,
                    day_of_week text
                )""")

    c.executemany("""INSERT INTO divvybikedata(ride_id, rideable_type,
                    start_station_name, end_station_name, member_casual, time_hours,
                    year_month, day_of_week) VALUES (?,?,?,?,?,?,?,?)""", altered_data)
        
    rows = c.execute("""SELECT *
                FROM divvybikedata LIMIT 10""").fetchall()
    print(rows)

    ##Save new table as a csv file.
    c.execute("""SELECT * FROM divvybikedata""")
    with open("cleaned_bike_data_202203_to_202302.csv", 'w', newline = '') as csv_file:
              csv_writer = csv.writer(csv_file)
              csv_writer.writerow([i[0] for i in c.description])
              csv_writer.writerows(c)


    ##Link to the visualizations in Tableau Public;
    ##https://public.tableau.com/app/profile/collin.mcclendon/viz/CyclisticBikeData_16690709427350/Sheet8#1
