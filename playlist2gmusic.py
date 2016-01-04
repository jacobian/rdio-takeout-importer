import re
import csv
import click
import getpass
import pathlib
import gmusicapi

@click.command()
@click.option('--username', prompt='Google username (usually, email)')
@click.option('--password', prompt='Google password', hide_input=True)
@click.option('--public/--private', default=True)
@click.argument('playlist', type=click.Path(exists=True))
def import_playlist(username, password, public, playlist):
    gmusic = gmusicapi.Mobileclient()
    gmusic.login(username, password, gmusicapi.Mobileclient.FROM_MAC_ADDRESS)
    
    # Delete an existing playlist if it already exists. This is a bit easier
    # than trying to de-dup tracks.
    playlist_name = pathlib.Path(playlist).stem.replace('_', ' ')
    existing_playlists = {p['name']: p['id'] for p in gmusic.get_all_playlists()}
    if playlist_name in existing_playlists:
        click.confirm('Playlist already exists; continuing will delete it and start over. OK?', abort=True)
        gmusic.delete_playlist(existing_playlists[playlist_name])
    
    playlist_track_ids = []

    # Technique for finding tracks:
    #   1. search for "{artist} {track}"
    #   2. for each song hit, calcuate a "score" based on how many fields
    #      (track name, artist name, album name, track number) match.
    #   3. choose the highest score

    with click.progressbar(list(csv.DictReader(open(playlist))), label="Finding tracks") as tracks:
        for track in tracks:
            search_results = gmusic.search_all_access('{Artist} {Name}'.format(**track))['song_hits']
            candidates = [r['track'] for r in search_results]
            scored_candidates = []
            for candidate in candidates:
                score = sum([
                    normalize(candidate['album']) == normalize(track['Album']),
                    normalize(candidate['artist']) == normalize(track['Artist']),
                    normalize(candidate['title']) == normalize(track['Name']),
                    str(candidate['trackNumber']) == track['Track Number'],
                ])
                # Don't include tracks with a score of 0.
                if score:
                    scored_candidates.append((score, candidate))

            if not scored_candidates:
                click.secho("Can't find: {Artist} - {Name}".format(**track), fg='yellow')
                continue

            match = max(scored_candidates)[1]
            playlist_track_ids.append(match['storeId'])

        playlist_id = gmusic.create_playlist(playlist_name, public=public)
        gmusic.add_songs_to_playlist(playlist_id, playlist_track_ids)

def normalize(s):
    return re.sub(r'\(.*?\)', '', s.lower()).strip()

if __name__ == '__main__':
    import_playlist()