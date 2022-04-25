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

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
# client_credentials_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, username=username, client_id=cid, client_secret=secret, redirect_uri=redirect_uri, open_browser= False)
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
    track_info = sp.track(id_sp)
    features = sp.audio_features(id_sp)

    #track info
    name = track_info['name']
    artist = track_info['album']['artists'][0]['name']
    #features
    tempo = features[0]['tempo']
    danceability = features[0]['danceability']
    speechiness = features[0]['speechiness']
    liveness = features[0]['liveness']

    track = [name, artist, tempo, danceability, speechiness,liveness]
    return track


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_table(ids,start, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify (song_id INTEGER PRIMARY KEY, title TEXT, artist TEXT, tempo INTEGER, danceability INTEGER, speechiness INTEGER, liveness INTEGER)")
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

         cur.execute("INSERT OR IGNORE INTO Spotify (song_id, title, artist, tempo, danceability, speechiness, liveness) VALUES (?, ?, ?, ?, ?, ?, ?)", (song_id, title, artist, tempo, danceability, speechiness, liveness))
    conn.commit()

def join_3_databases(ranking, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Averages (ranking INTEGER PRIMARY KEY, avg_tempo INTEGER, avg_danceability INTEGER, avg_speechiness INTEGER, avg_liveness INTEGER)")

    cur.execute("SELECT Spotify.tempo, Spotify.danceability, Spotify.speechiness, Spotify.liveness FROM Discogs JOIN Spotify ON Discogs.song_id == Spotify.song_id WHERE Discogs.ranking == ?", (ranking, ))

    avg_tempo = 0
    avg_danceability = 0
    avg_speechiness = 0
    avg_liveness = 0

    for row in cur:
        print("discogs:", row)
        avg_tempo += row[0]
        avg_danceability += row[1]
        avg_speechiness += row[2]
        avg_liveness += row[3]

    cur.execute("SELECT Spotify.tempo, Spotify.danceability, Spotify.speechiness, Spotify.liveness FROM Deezer JOIN Spotify ON Deezer.song_id == Spotify.song_id WHERE Deezer.ranking == ?", (ranking, ))

    for row in cur:
        print("deezer:", row)
        avg_tempo += row[0]
        avg_danceability += row[1]
        avg_speechiness += row[2]
        avg_liveness += row[3]

    avg_tempo = avg_tempo / 8
    avg_danceability = avg_danceability / 8
    avg_speechiness = avg_speechiness / 8
    avg_liveness = avg_liveness / 8

    cur.execute("INSERT OR IGNORE INTO Averages (ranking, avg_tempo, avg_danceability, avg_speechiness, avg_liveness) VALUES (?, ?, ?, ?, ?)", (ranking, avg_tempo, avg_danceability, avg_speechiness, avg_liveness))
    conn.commit()

def main():
    cur, conn = setUpDatabase('music.db')

    Discogs_top25_US = getTrackIDs('yuriii','2OSzXp9nSHyUgC9WviQEHo')
    Discogs_top25_FR = getTrackIDs('yuriii','3WJ0FDVrJxG3gpE3G7Y34c')
    Discogs_top25_CA = getTrackIDs('yuriii','1qrRuRY6juGQrItbR7Y3Yt')
    Discogs_top25_UK = getTrackIDs('yuriii','1wEqjX4fSRpssepF7RC2a5')

    Deezer_top25_US = getTrackIDs('yuriii','5ZC9rbYk5S0jpkxqOxr1YO')
    Deezer_top25_FR = getTrackIDs('yuriii','1HYZlXddhKQn1qXGpSM2IP')
    Deezer_top25_CA = getTrackIDs('yuriii','51kb6iDc0hdaj8mJyVvMaI')
    Deezer_top25_UK = getTrackIDs('yuriii','07B2KrdbdsuVAPrXTx6MU5')

    set_up_table(Discogs_top25_US, 0, cur, conn)
    set_up_table(Discogs_top25_FR, 25, cur, conn)
    set_up_table(Discogs_top25_CA, 50, cur, conn)
    set_up_table(Discogs_top25_UK, 75, cur, conn)

    set_up_table(Deezer_top25_US, 100, cur, conn)
    set_up_table(Deezer_top25_FR, 125, cur, conn)
    set_up_table(Deezer_top25_CA, 150, cur, conn)
    set_up_table(Deezer_top25_UK, 175, cur, conn)

    for i in range(1, 26):
        join_3_databases(i, cur, conn)


if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)  
