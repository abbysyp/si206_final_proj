from cgitb import text
from curses.panel import top_panel
from itertools import count
from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest
import sqlite3

def get_discog_songs():
    """
    Return a list of dictionaries of the top 25 songs on Discogs for the given country using BeautifulSoup
    """

    countries = ['US', 'France', 'Canada', 'UK']
    top_25_songs = []

    for country in countries:
        url = f'https://www.discogs.com/search/?sort=have%2Cdesc&ev=em_tr&format_exact=Single&country_exact={country}'
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        song_titles = soup.find_all('a', class_='search_result_title')
        song_artists = soup.find_all('h5')

        for i in range(0, 25):
            top_25_songs.append(
                {
                    'ranking': i + 1,
                    'title': song_titles[i].text,
                    'artist': song_artists[i].find('a').text,
                    'country': country
                }
            )
    return top_25_songs

def setUpDatabase(db_name):
    '''
    Takes the database 'music.db' as a parameter and sets up the database, and returns cur and conn
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_discogs_table(data, cur, conn):
    # cur.execute("DROP TABLE Discogs")
    cur.execute("CREATE TABLE IF NOT EXISTS Discogs (song_id INTEGER PRIMARY KEY, ranking INTEGER, country TEXT, title TEXT, artist TEXT)")

    #select max id (last one put in db)
    cur.execute('SELECT song_id FROM Discogs WHERE song_id  = (SELECT MAX(song_id) FROM Discogs)')
    start = cur.fetchone()
    if (start!= None):
        start = start[0]
    else:
        start = 0

    id_counter = start
    for song in data[start:start+25]:

        id_counter = id_counter + 1
        song_id = id_counter
        ranking = song['ranking']
        country = song['country']
        title = song['title']
        artist = song['artist']
        
        cur.execute("INSERT OR IGNORE INTO Discogs (song_id, ranking, country, title, artist) VALUES (?, ?, ?, ?, ?)", (song_id, ranking, country, title, artist))

    conn.commit()

if __name__ == '__main__':
    cur, conn = setUpDatabase('music.db')

    top_discogs = get_discog_songs()

    set_up_discogs_table(top_discogs, cur, conn)
