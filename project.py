import sys
import spotipy
import sqlite3
import requests
import unittest
import os
import json
import csv
from spotipy.oauth2 import SpotifyClientCredentials

# conn = sqlite3.connect()
# cur = conn.cursor()

# cur.execute('SELECT title, plays FROM Tracks__NAME')
# for row in cur:
#     print(row)
# cur.close()

cid = '23e1af0888aa480091c4a690ac772352'
secret = '7df9c34ebea34a009787cf22251a4728'
username = 'yuriii'
scope = 'user-library-read'
redirect_uri = 'http://localhost:8888/callback'

# client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
client_credentials_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, username=username, client_id=cid, client_secret=secret, redirect_uri=redirect_uri, open_browser= False)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def getTrackIDs(user,playlist_id):
    ids= []
    playlist = sp.user_playlist(user,playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        ids.append(track['id'])
    return ids

# ids = getTrackIDs('yuriii','3H5OVme5Omrwrzc8zBDpKp')
# print(len(ids))
# print(ids)

def getTrackFeatures(id_sp):
    meta = sp.track(id_sp)
    features = sp.audio_features(id_sp)

    #name
    name = meta['name']
    artist = meta['album']['artists'][0]['name']
    #features
    tempo = features[0]['tempo']
    danceability = features[0]['danceability']
    speechiness = features[0]['speechiness']
    liveness = features[0]['liveness']

    track = [name, artist, tempo, danceability, speechiness,liveness]
    return track

# feature = getTrackFeatures('1z3ugFmUKoCzGsI6jdY4Ci')
# print(feature)

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_table(ids, start, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Discogs (song_id INTEGER PRIMARY KEY, title TEXT, artist TEXT, tempo TEXT, danceability TEXT, speechiness TEXT, liveness TEXT)")
    song_id = start
    
    for id_sp in ids:
        features = getTrackFeatures(id_sp)
        song_id = song_id + 1
        title =  features[0]
        artist = features[1]
        tempo = features[2]
        danceability = features[3]
        speechiness = features[4]
        liveness = features[5]
        cur.execute("INSERT OR IGNORE INTO Discogs (song_id, title, artist, tempo, danceability, speechiness, liveness) VALUES (?, ?, ?, ?, ?, ?, ?)", (song_id, title, artist, tempo, danceability, speechiness, liveness))
    conn.commit

def main():
    cur, conn = setUpDatabase('features.db')

    Discogs_top25_US = getTrackIDs('yuriii','2OSzXp9nSHyUgC9WviQEHo')
    Discogs_top25_FR = getTrackIDs('yuriii','3WJ0FDVrJxG3gpE3G7Y34c')
    Discogs_top25_CA = getTrackIDs('yuriii','1qrRuRY6juGQrItbR7Y3Yt')
    Discogs_top25_UK = getTrackIDs('yuriii','1wEqjX4fSRpssepF7RC2a5')

    set_up_table(Discogs_top25_US, 0, cur, conn)
    set_up_table(Discogs_top25_FR, 0, cur, conn)
    set_up_table(Discogs_top25_CA, 0, cur, conn)
    set_up_table(Discogs_top25_UK, 0, cur, conn)

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)  
