"""
Convert an rdio export csv to sqlite3
"""

import sqlite3
import pathlib
import click
import collections
import csv

def main():
    here = pathlib.Path(__file__).parent
    collection_db_file = here / 'collection.sqlite3'
    csv_file = here / 'collection.csv'

    if collection_db_file.exists():
        click.secho("collection.sqlite3 already exists, bailing", fg='red')
        return 

    db = sqlite3.connect(str(collection_db_file))
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE collection (
        artist text,
        album text,
        track_count int,
        skip boolean,
        complete boolean
    );''')

    if not csv_file.exists():
        click.secho("collection.csv doesn't exist, bailing", fg=red)
        return

    artist_albums = collections.Counter()
    for row in csv.DictReader(open(str(csv_file))):
        artist_albums[(row['Artist'], row['Album'])] += 1

    for ((artist, album), count) in artist_albums.most_common():
        artist = artist.decode('utf8')
        album = album.decode('utf8')
        cursor.execute('''INSERT INTO collection
                        (artist, album, track_count, skip, complete)
                      VALUES
                        (?, ?, ?, 0, 0)''', [artist, album, count])

    db.commit()
    db.close()

if __name__ == '__main__':
    main()