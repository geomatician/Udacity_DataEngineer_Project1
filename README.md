# Project 1: Data Modeling With Postgres

# Purpose of database in context of Sparkify and their goals

Sparkify wants to analyze data that they are collecting on songs and user activity in their music streaming application.
Currently, all of their data resides within JSON files of two types- song data files and log data files. Song data files contain information about songs and artists. Log data files contain information about application users and times. The analytics team at Sparkify wants to find a better way to organize and query this data to generate analytics. This can be done by setting up an ETL pipeline that 1) reads data from the JSON files, 2) transforms it into a useful structure for insertion into a database in PostgreSQL, and 3) loads it into a set of organized tables, after which optimized queries can be run on the database. With an enhanced organization of data, the analytics team can run customized, ad-hoc queries and generate useful analytics from the data. 

# How to run the Python scripts

You should already have a PostgreSQL database user with a username of 'student' and a password of 'student' created prior to running these scripts, since these scripts use this user to create and load data into the tables. This user should have the 'CreateDB' role assigned to it that allows it to create the sparkify database. 

First, clone the Git repository to a directory on your local machine. 

Then, navigate (cd) into this directory and run the commands in the following order:

python create_tables.py
python etl.py

Python 3.9.13 was used for this project. Prior to running the above scripts, ensure that the psycopg2 and pandas packages are installed within the current environment. 

You can then run the commands inside test.ipynb to verify that the tables were populated with data and run custom queries and sanity checks on these tables.

# Files in repository

1) data folder - this contains the 'song data' and 'log data' files obtained from the Million Song Dataset  and generated from an event simulator, respectively. There are two folders within this folder- one for song data and one for log data. 
2) create_tables.py - this creates the sparkify database, establishes a connection to it, drops all tables if they exist, and (re) creates these tables in the database. After running this script, a new database named 'sparkify' should be created that contains 5 empty tables- artists, songplays, songs, time, and users. 
3) etl.py - this will load the data from the song and log JSON files into tables created by create_tables.py.
4) etl.ipynb - this is a Jupyter Notebook that was used to develop the ETL processes for each of the tables and to develop the script etl.py. 
5) sql_queries.py - this contains SQL queries to create tables and insert data into these tables for each of the five tables created in this project. These queries are used in create_tables.py and etl.py. 
6) test.ipynb - this is a Juputer Notebook that was used to run sanity tests on the tables after they were created and populated with data. 

# Database schema design and ETL pipeline

The data gets eventually stored into five separate tables: songplays, songs, artists, users, and time. Each table has its own primary key that is unique and not null by definition. Some of the tables also have foreign keys that allow them to be associated with other tables in the database: for example, the songplays table has user_id, artist_id, and song_id fields, and the songs table has an artist_id field. With the combination of their primary and foreign keys through joins, customized SQL queries can be written to generate analytics across these tables. 

The data types of the fields within each table have been set properly. Furthermore, NOT NULL, PRIMARY KEY, and ON CONFLICT constraints have been introduced into sql_queries.py to prevent duplicates and non-null values from being populated into the tables. The ETL pipeline contained within etl.py, when run, extracts data from the JSON files, transforms them into an appropriate structure before the load, and loads this construct into the database. 

The songplays table is the core table (i.e. fact table) that contains foreign keys to the songs, artists, users, and time tables (i.e. dimension tables).  Together, they form a star schema with the songplays table at the center, and the other four tables around it. A star schema in the way organized in this project provides several benefits: 1) it makes queries easier with simple joins 2) we can perform aggregations on our data, and 3) we can relate the fact table with the dimension tables to perform cross-table analysis ; the fact table contains foreign keys which by definition are primary keys of the dimension tables. The dimension tables contain additional information about each type of entity- i.e. song, artist, user, and time, whereas the fact table displays the relationships between these different entities in one table using foreign keys. 

This serves as a justification for the database schema design and ETL pipeline. 


# Example queries and results 

These are just some example queries that can be run on the database to yield useful analytics:

1) Which areas in the United States users are most users listening to songs on their app from? 

SELECT location, COUNT(*) as counts
FROM songplays
GROUP BY location
ORDER BY counts DESC

This shows that the top three places where users are listening from are San Francisco, CA (691 songplays), Portland, ME (665 songplays), and Lansing, MI (557 songplays). 

2) Which gender most listens to songs on their app? By joining the fact table songplays with the dimension table users, we can get this information. 

SELECT gender, COUNT(*) FROM
songplays JOIN users ON songplays.user_id = users.user_id
GROUP BY gender

This shows that more females (4887) than males (1933) are active.

3) Are most users having a free or paid subscription?

SELECT level, COUNT(level)
FROM songplays
GROUP BY level

This shows that there are more paid subscribers (5591) than free subscribers (1229). 