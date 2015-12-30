# -*- coding: utf-8 -*-
import base64
import click
import pathlib
import gmusicapi
import sqlite3
import time
import urllib
from more_itertools import chunked
from pprint import pprint

# FILL THESE IN YOURSELF:
USERNAME = 'jacob@jacobian.org'
PASSWORD = 'dacvvtwwtebwwhag'

class SkipAlbum(Exception):
    pass

def main():
    gmusic = gmusicapi.Mobileclient()
    gmusic.login(USERNAME, PASSWORD, gmusicapi.Mobileclient.FROM_MAC_ADDRESS)

    here = pathlib.Path(__file__).parent
    collection_db_file = here / 'collection.sqlite3'
    if not collection_db_file.exists():
        click.secho("collection.sqlite3 doesn't exist, run rdio_export_to_sqlite3.py first", fg='red')
        return

    db = sqlite3.connect(str(collection_db_file))
    cursor = db.cursor()
    cursor.execute('''SELECT artist, album
                      FROM collection
                      WHERE skip = 0
                      AND complete = 0
                      AND track_count > 5
                      ORDER BY track_count DESC''')

    all_albums = cursor.fetchall()
    for i, (artist, album) in enumerate(all_albums):
        print_header(artist, album, i, len(all_albums))
        results = gmusic.search_all_access(artist + ' ' + album)['album_hits']
        if not results:
            click.secho("Can't find it, fixup please.", fg='yellow')
            fixed_artist = click.prompt('Artist'.format(artist), default=artist)
            fixed_album = click.prompt('Album'.format(album), default=album)
            results = gmusic.search_all_access(fixed_artist + ' ' + fixed_album)['album_hits']
            if not results:
                handle_not_found(db, artist, album)
                continue

        # swizzle results into a slightly more usable form
        results = [r['album'] for r in results]

        try:
            album_object = select_album(artist, album, results, i, len(all_albums))
        except SkipAlbum:
            handle_not_found(db, artist, album, prompt=False)
            continue

        if album_object:
            add_to_gmusic(db, gmusic, album_object, artist, album)
        else:
            handle_not_found(db, artist, album)

    db.close()


def print_header(artist, album, current, total):
    click.clear()
    title = u'{0} - {1}'.format(artist, album)
    progress = u'{0}/{1}'.format(current+1, total)
    term_width, term_height = click.get_terminal_size()
    pad_width = (term_width - len(title) - len(progress)) - 10
    header_template = u'=== {title} {pad} {progress} ==='
    click.secho(
        header_template.format(
            title=title,
            pad='=' * pad_width,
            progress=progress,
        ),
        bg='blue', fg='white'
    )


def handle_not_found(db, artist, album, prompt=True):
    if prompt:
        click.secho('Damn, not found.', fg='yellow')
        skip = click.confirm('Skip next time?', default=True)
    else:
        skip = True
    if skip:
        cursor = db.cursor()
        cursor.execute('''UPDATE collection SET skip = 1
                          WHERE artist = ? AND album = ?''', [artist, album])
        db.commit()


def select_album(original_artist, original_album, albums, current_position, total_number):
    for album in albums:
        print_header(original_artist, original_album, current_position, total_number)
        click.secho(u'\nFound: "{0}"\n'.format(album['name']), fg='green')
        print imgcat(album['albumArtRef'])

        action = None
        while action not in ('y', 'n', 's'):
            actions = '/'.join(under_first(s) for s in ('yes', 'next', 'skip'))
            action = click.prompt('\nAdd to collection? ' + actions, default='y')
            action = action[0].lower()

        if action == 'y':
            return album
        elif action == 's':
            raise SkipAlbum()
        else:
            continue

def add_to_gmusic(db, gmusic, album, original_artist, original_album):
    album = gmusic.get_album_info(album['albumId'], include_tracks=True)
    track_ids = [t['storeId'] for t in album['tracks']]
    click.secho('Adding {0} tracks to Google Music...'.format(len(track_ids)))
    for t in track_ids:
        gmusic.add_aa_track(t)
    
    cursor = db.cursor()
    cursor.execute('''UPDATE collection SET complete = 1
                      WHERE artist = ? AND album = ?''',
                   [original_artist, original_album])
    db.commit()
    click.secho('Done ', fg='green', nl=False)


def imgcat(url):
    content = base64.encodestring(urllib.urlopen(url).read())
    text = "\033]1337;File=inline=1;size={0};px:{1}\a"
    return text.format(str(len(content)), content)


def under_first(s):
    return click.style(s[0], underline=True) + s[1:]


if __name__ == '__main__':
    try:
        main()
    except click.exceptions.Abort:
        pass
