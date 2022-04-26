
import requests
import json
import sys
import os
import sqlite3
import unittest
import csv
import datetime
import jwt

'''
1. Go to https://connect.deezer.com/oauth/auth.php?app_id=YOUR_APP_ID&redirect_uri=YOUR_REDIRECT_URI&perms=basic_access,email
(Yuna's appId:537442, redirectURL: https://theappreciationengine.com/DeezerAuthenticator_Controller )
(https://connect.deezer.com/oauth/auth.php?app_id=537442&redirect_uri=https://theappreciationengine.com/DeezerAuthenticator_Controller&perms=basic_access,email)
2. Click "continue" if prompted yunat account
--> on the url bar, find the code="**"
** is the auth code
3. On the url bar, type
https://connect.deezer.com/oauth/access_token.php?app_id=537442&secret=4d5f70ae842906d48ae6521d946d5654&code=***
For the ***, enter the auth code from 2
--> You will get the access_token. This is valid for 3600 seconds. 
'''

def top_25_songs_search(country):
'''
Takes a country (US, UK, Canada, or France), assign the corresponding id. It then uses the Deezer API to obtain song information for the top 25 songs of the country. It then finds the ranking, title, artist, and country of each song obtained and returns a list of dictionaries. ex. [{ranking: 1, title: ___, artists: ____, country: ___}, {...}]
'''
    if country == 'US':
        id = '1313621735'
    elif country == 'Canada':
        id = '1652248171'
    elif country == 'France':
        id = '1109890291'
    elif country == 'UK':
        id = '7241549564'

    token = 'frdyDKjLNK64GahOsa0VAy5WN7rnJzvXgisjccFhqskm7ga91zx'
    baseurl = 'https://api.deezer.com/playlist/' + id
    param = {'limit': 25, 'access_token': token}
    response = requests.get(baseurl, params = param)
    response_json = response.json()
    all_results = response_json

    songs = []
    i = 0
    for i in range(0,25):
        songs.append({'ranking' : i + 1,'title' : all_results['tracks']['data'][i]['title'],'artists' : all_results['tracks']['data'][i]['artist']['name'], 'country': country})   
    return songs
    '''print(all_results)'''

def setUpDatabase(db_name):
'''
Takes the database 'music.db' as a [ara,eter. sets up the database, and returns cur and conn
'''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_deezer_table(data, start, cur, conn):
'''
Sets up the Deezer table that will go into the 'music1.db' database. It takes the list of tuples returned by top_25_songs_search and put them in a table (1 country, 25 songs at a time) that has the following values: song_id (shared key), ranking, country, title, artist.
'''
    cur.execute("CREATE TABLE IF NOT EXISTS Deezer (song_id INTEGER PRIMARY KEY, ranking INTEGER, country TEXT, title TEXT, artist TEXT)")
    song_id = start

    for song in data:

        song_id = song_id + 1
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
    cur.execute("DROP TABLE Deezer")

    top25_US = top_25_songs_search('US')
    top25_FR = top_25_songs_search('France')
    top25_CA = top_25_songs_search('Canada')
    top25_UK = top_25_songs_search('UK')

    set_up_deezer_table(top25_US, 100, cur, conn)
    set_up_deezer_table(top25_FR, 125, cur, conn)
    set_up_deezer_table(top25_UK, 150, cur, conn)
    set_up_deezer_table(top25_CA, 175, cur, conn)

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)
