import sys
import spotipy
import sqlite3
import requests
import unittest
import os
import json
import csv
from spotipy.oauth2 import SpotifyClientCredentials

cid = '23e1af0888aa480091c4a690ac772352'
secret = '7df9c34ebea34a009787cf22251a4728'
username = 'yuriii'
scope = 'user-library-read'
redirect_uri = 'http://localhost:8888/callback'

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
#client_credentials_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, username=username, client_id=cid, client_secret=secret, redirect_uri=redirect_uri, open_browser= False)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def getTrackIDs():
    user = 'yuriii'
    playlists = ['2OSzXp9nSHyUgC9WviQEHo','3WJ0FDVrJxG3gpE3G7Y34c', '1qrRuRY6juGQrItbR7Y3Yt', '1wEqjX4fSRpssepF7RC2a5', '07B2KrdbdsuVAPrXTx6MU5', '1HYZlXddhKQn1qXGpSM2IP', '51kb6iDc0hdaj8mJyVvMaI', '5ZC9rbYk5S0jpkxqOxr1YO']
    ids= []
    for playlist_id in playlists:
        playlist = sp.user_playlist(user,playlist_id)
        for item in playlist['tracks']['items']:
            track = item['track']
            ids.append(track['id'])
            if len(ids)==25:
                break
    return ids

def getTrackFeatures(id_sp):
    track_info = sp.track(id_sp)
    features = sp.audio_features(id_sp)
    #name
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

def set_up_table(ids, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify (song_id INTEGER PRIMARY KEY, title TEXT, artist TEXT, tempo INTEGER, danceability INTEGER, speechiness INTEGER, liveness INTEGER)")
    cur.execute('SELECT song_id FROM Spotify WHERE song_id = (SELECT MAX(song_id) FROM Spotify)')
    start = cur.fetchone()

    if (start!= None):
        start = start[0]
    else:
        start = 0
    id_counter = start
    for id_sp in ids[start:start+25]:
         features = getTrackFeatures(id_sp)
         id_counter = id_counter + 1
         song_id = id_counter
         title =  features[0]
         artist = features[1]
         tempo = features[2]
         danceability = features[3]
         speechiness = features[4]
         liveness = features[5]

         cur.execute("INSERT OR IGNORE INTO Spotify (song_id, title, artist, tempo, danceability, speechiness, liveness) VALUES (?, ?, ?, ?, ?, ?, ?)", (song_id, title, artist, tempo, danceability, speechiness, liveness))
    conn.commit()

def drop_table(cur, conn):
    cur.execute('DROP TABLE Spotify')
    conn.commit()

def join_3_databases(info_dict, ranking, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Averages (ranking INTEGER PRIMARY KEY, avg_tempo INTEGER, avg_danceability INTEGER, avg_speechiness INTEGER, avg_liveness INTEGER)")

    cur.execute("SELECT Spotify.tempo, Spotify.danceability, Spotify.speechiness, Spotify.liveness FROM Discogs JOIN Spotify ON Discogs.song_id == Spotify.song_id WHERE Discogs.ranking == ?", (ranking, ))

    avg_tempo = 0
    avg_danceability = 0
    avg_speechiness = 0
    avg_liveness = 0

    for row in cur:
        avg_tempo += row[0]
        avg_danceability += row[1]
        avg_speechiness += row[2]
        avg_liveness += row[3]

    cur.execute("SELECT Spotify.tempo, Spotify.danceability, Spotify.speechiness, Spotify.liveness FROM Deezer JOIN Spotify ON Deezer.song_id == Spotify.song_id WHERE Deezer.ranking == ?", (ranking, ))

    for row in cur:
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

    info_dict[ranking] = [avg_tempo, avg_danceability, avg_speechiness, avg_liveness]

def printAverages(info_dict, file):
    source_dir = os.path.dirname(__file__)
    full_path = os.path.join(source_dir, file)
    out_file = open(full_path, "w")
    with open(file) as f:
        csv_writer = csv.writer(out_file, delimiter=",", quotechar='"')
        out_file.write('Average Spotify statistics for the top 25 songs in US, France, Canada, and UK on Deezer and Discogs\n')
        for key, item in info_dict.items():
            out_file.write('#' + str(key) + ": ")
            out_file.write('Tempo - ' + str(item[0]) + ', ')
            out_file.write('Danceability - ' + str(item[1]) + ', ')
            out_file.write('Speechiness - ' + str(item[2]) + ', ')
            out_file.write('Liveness - ' + str(item[3]) + '\n')

def main():
    cur, conn = setUpDatabase('music.db')
    track_ids = getTrackIDs()
    set_up_table(track_ids, cur,conn)

    all_info = {}
    for i in range(1, 26):
        join_3_databases(all_info, i, cur, conn)
    printAverages(all_info, 'results.txt')

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)  
