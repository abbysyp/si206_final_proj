
import requests
import json
import sys
import os
import sqlite3
import unittest
import csv
import datetime
import jwt


'''def read_cache(CACHE_FNAME):
    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") 
        cache_contents = cache_file.read()  
        CACHE_DICTION = json.loads(cache_contents) 
        cache_file.close() 
        return CACHE_DICTION
    except:
        CACHE_DICTION = {}
        return CACHE_DICTION'''
'''
1. Go to https://connect.deezer.com/oauth/auth.php?app_id=YOUR_APP_ID&redirect_uri=YOUR_REDIRECT_URI&perms=basic_access,email
(Yuna's appId:537442, redirectURL: https://theappreciationengine.com/DeezerAuthenticator_Controller )
(https://connect.deezer.com/oauth/auth.php?app_id=537442&redirect_uri=https://theappreciationengine.com/DeezerAuthenticator_Controller&perms=basic_access,email)
2. Click "continue" if prompted yunat account
--> on the url bar, find the code="**"
fr3d68969fde9d5427807046d156d4b8
** is the auth code
3. On the url bar, type
https://connect.deezer.com/oauth/access_token.php?app_id=537442&secret=4d5f70ae842906d48ae6521d946d5654&code=***
For the ***, enter the auth code from 2
--> You will get the access_token. This is valid for 3600 seconds. 
'''

def get_deezer_songs():
    '''
    Loops through ids_for_each_country list for each id corresponding with 4 countries. 
    It then uses the Deezer API to obtain song information for the top 25 songs of the country. It then finds the ranking, 
    title, artist, and country of each song obtained and returns a list of dictionaries. 
    ex. [{ranking: 1, title: ___, artists: ____, country: ___}, {...}]'''

    ids_for_each_country = ['1313621735', '1652248171', '1109890291', '7241549564']
    songs = []

    for id in ids_for_each_country:
        token = 'frBeZFVkgg9rDnWEXnCbV3w0Twd75Dzzfi87ctgoLpAfJCaddNz'
        baseurl = 'https://api.deezer.com/playlist/' + id
        param = {'limit': 25, 'access_token': token}
        response = requests.get(baseurl, params = param)
        response_json = response.json()
        all_results = response_json

        if id == '1313621735':
            country = 'US'
        elif id == '1652248171':
            country = 'Canada'
        elif id == '1109890291':
            country = 'France'
        elif id == '7241549564':
            country = 'UK'

        
        i = 0
        for i in range(0,25):
            songs.append({'ranking' : i + 1,'title' : all_results['tracks']['data'][i]['title'],'artists' : all_results['tracks']['data'][i]['artist']['name'], 'country': country})
    print(songs)
    return songs
    

def setUpDatabase(db_name):
    '''
    Takes the database 'music1.db' as a [ara,eter. sets up the database, and returns cur and conn
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_deezer_table(data, cur, conn):
    '''
    Sets up the Deezer table that will go into the 'music.db' database. 
    It takes the list of tuples returned by get_deezer_songs and put them in a table 
    (25 songs at a time/per run) that has the following values: 
    song_id (shared key), ranking, country, title, artist.
    Obtain the last song_id in the database to identify where in data(dictionary) to start from. 
    '''

    cur.execute("CREATE TABLE IF NOT EXISTS Deezer (song_id INTEGER PRIMARY KEY, ranking INTEGER, country TEXT, title TEXT, artist TEXT)")

    cur.execute('SELECT song_id FROM Deezer WHERE song_id  = (SELECT MAX(song_id) FROM Deezer)')
    start = cur.fetchone()
    if (start != None):
        start = start[0]
    else: start = 0

    id_counter = start

    for song in data[start:start + 25]:

        id_counter += 1
        song_id = id_counter
        ranking = song['ranking']
        country = song['country']
        title = song['title']
        artist = song['artists']
        
        cur.execute("INSERT OR IGNORE INTO Deezer (song_id, ranking, country, title, artist) VALUES (?, ?, ?, ?, ?)", (song_id, ranking, country, title, artist))

    conn.commit()


def main():
    '''
    calls the above functions.
    '''
    
    cur, conn = setUpDatabase('music.db')

    top_deezer = get_deezer_songs()

    set_up_deezer_table(top_deezer, cur, conn)


if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)
