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
    '''This function looks through each playlists gathered by top 25 songs in the Discogs and Deezer Databse
    and find all the song IDs in these database'''
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
    '''This function collects all the song features including 
    song name, artist, tempo, danceability, speechiness, liveliness, and loudness using the song IDs'''
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
    loudness = features[0]['loudness']

    track = [name, artist, tempo, danceability, speechiness,liveness,loudness]
    return track

def setUpDatabase(db_name):
    '''This function takes the database 'music.db' as a parameter, sets up the database, 
    and returns cur and conn'''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_table(ids, cur, conn):
    '''This function sets up the Spotify info and features table under 'music.db' and takes in all the song features information 
    and stores it in the table 25 songs at a time. This code needs to be run 8 times'''
    
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyINFO (song_id INTEGER PRIMARY KEY, title TEXT, artist TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyFEATURES (song_id INTEGER PRIMARY KEY, tempo INTEGER, danceability INTEGER, speechiness INTEGER, liveness INTEGER, loudness INTEGER)")
    cur.execute('SELECT song_id FROM SpotifyINFO WHERE song_id = (SELECT MAX(song_id) FROM SpotifyINFO)')
    cur.execute('SELECT song_id FROM SpotifyFEATURES WHERE song_id = (SELECT MAX(song_id) FROM SpotifyFEATURES)')
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
         loudness = features[6]

         cur.execute("INSERT OR IGNORE INTO SpotifyINFO (song_id, title, artist) VALUES (?, ?, ?)", (song_id, title, artist))
         cur.execute("INSERT OR IGNORE INTO SpotifyFEATURES (song_id, tempo, danceability, speechiness, liveness, loudness) VALUES (?, ?, ?, ?, ?, ?)", (song_id, tempo, danceability, speechiness, liveness, loudness))
    conn.commit()

def drop_table(name, cur, conn):
    '''This additional function is used to drop selected table if the database is not loading properly'''
    cur.execute(f"DROP TABLE {name}")
    conn.commit()

def join_3_databases(info_dict, ranking, cur, conn):
    '''This function takes in an empty dictionary, a specific ranking, cur, and conn and creates the Averages table in the database 'music.db'.
    It then uses JOIN to select Spotify statistics for songs that are of that ranking (e.g. all of the #1 songs) from Discogs and Deezer tables.
    After each JOIN, the function loops through the selected songs to find the accumulated tempo, danceability, speechiness, liveness, and loudness scores.
    Then, these values are divided by 8 (e.g. 4 #1 songs from Discogs + 4 #1 songs from Deezer) to find the averages for each ranking and stores
    this information into the Averages table as well as into the passed in dictionary.'''
    
    cur.execute("CREATE TABLE IF NOT EXISTS Averages (ranking INTEGER PRIMARY KEY, avg_tempo INTEGER, avg_danceability INTEGER, avg_speechiness INTEGER, avg_liveness INTEGER, avg_loudness INTEGER)")

    cur.execute("SELECT SpotifyFEATURES.tempo, SpotifyFEATURES.danceability, SpotifyFEATURES.speechiness, SpotifyFEATURES.liveness, SpotifyFEATURES.loudness FROM Discogs JOIN SpotifyFEATURES ON Discogs.song_id == SpotifyFEATURES.song_id WHERE Discogs.ranking == ?", (ranking, ))

    avg_tempo = 0
    avg_danceability = 0
    avg_speechiness = 0
    avg_liveness = 0
    avg_loudness = 0

    for row in cur:
        avg_tempo += row[0]
        avg_danceability += row[1]
        avg_speechiness += row[2]
        avg_liveness += row[3]
        avg_loudness += row[4]


    cur.execute("SELECT SpotifyFEATURES.tempo, SpotifyFEATURES.danceability, SpotifyFEATURES.speechiness, SpotifyFEATURES.liveness, SpotifyFEATURES.loudness FROM Deezer JOIN SpotifyFEATURES ON Deezer.song_id == SpotifyFEATURES.song_id WHERE Deezer.ranking == ?", (ranking, ))

    for row in cur:
        avg_tempo += row[0]
        avg_danceability += row[1]
        avg_speechiness += row[2]
        avg_liveness += row[3]
        avg_loudness += row[4]

    avg_tempo = avg_tempo / 8
    avg_danceability = avg_danceability / 8
    avg_speechiness = avg_speechiness / 8
    avg_liveness = avg_liveness / 8
    avg_loudness = avg_loudness / 8

    cur.execute("INSERT OR IGNORE INTO Averages (ranking, avg_tempo, avg_danceability, avg_speechiness, avg_liveness, avg_loudness) VALUES (?, ?, ?, ?, ?,?)", (ranking, avg_tempo, avg_danceability, avg_speechiness, avg_liveness, avg_loudness))
    conn.commit()

    info_dict[ranking] = [avg_tempo, avg_danceability, avg_speechiness, avg_liveness, avg_loudness]

def printAverages(info_dict, file):
    '''This function takes in the dictionary now filled with information gathered from join_3_databases and writes it to the file 'results.text'
    in the format #X: Tempo - X, Danceability - X, Speechiness - X, Liveness - X, Loudness - X.''' 
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
            out_file.write('Liveness - ' + str(item[3]) + ',')
            out_file.write('Loudness - ' + str(item[4]) + '\n')

def main():
    '''calls the above functions.'''
    #Section 1- get Spotify features to database
    cur, conn = setUpDatabase('music.db')
    track_ids = getTrackIDs()
    set_up_table(track_ids, cur,conn)

    # Section 2- Calculate data & write text file
    all_info = {}
    for i in range(1, 26):
        join_3_databases(all_info, i, cur, conn)
    printAverages(all_info, 'results.txt')

    #Additional- drop necessary table to restart
    # drop_table('SpotifyINFO', cur,conn)
    # drop_table('SpotifyFEATURES', cur,conn)
    # drop_table('Averages', cur,conn)

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)  
