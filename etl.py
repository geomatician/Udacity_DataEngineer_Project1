import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    This function opens a song data file as a dataframe using it's filepath,
    extracts song and artist fields from the dataframe, and inserts them
    into the song and artist tables, respectively.
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = list(df[['song_id', 'title', 'artist_id', 'year',
                         'duration']].values[0])
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = list(df[['artist_id', 'artist_name', 'artist_location',
                           'artist_latitude', 'artist_longitude']].values[0])
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    This function opens a log file as a dataframe, keeps only the NextSong
    records, converts the timestamp into a datetime field, and then inserts
    records into the time, user, and songplay tables by looping over the rows
    in the dataframe.
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df.loc[df['page'] == 'NextSong']

    # convert timestamp column to datetime
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    t = df['ts']

    # insert time data records
    time_data = (t, t.dt.hour, t.dt.day, t.dt.isocalendar().week, t.dt.month,
                 t.dt.year, t.dt.weekday)
    column_labels = ('timestamp', 'hour', 'day', 'week', 'month', 'year',
                     'weekday')
    time_df = pd.DataFrame.from_dict(dict(zip(column_labels, time_data)))

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.ts, row.userId, row.level, songid, artistid,
                         row.sessionId, row.location, row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    This function loops over all of the json files inside of a directory,
    adds them to a list, and then loops over the list of files and calls
    either the process_song_file or process_log_file function to process
    the file depending on whether the file is a song file or log file.
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    This function connects to the sparkify database and then calls the
    process_data function to process all of the song and log files inside
    their respective folders within the data folder.
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student \
                             password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
