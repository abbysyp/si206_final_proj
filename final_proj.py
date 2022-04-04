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

def get_discog_songs(country):
    """
    Return a list of dictionaries of the top 25 songs on Discogs for the given country using BeautifulSoup
    """

    url = f'https://www.discogs.com/search/?sort=have%2Cdesc&ev=em_tr&format_exact=Single&country_exact={country}'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    song_titles = soup.find_all('a', class_='search_result_title')
    song_artists = soup.find_all('h5')

    top_25_songs = []

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
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_discogs_table(data, start, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Discogs (song_id INTEGER PRIMARY KEY, ranking INTEGER, country TEXT, title TEXT, artist TEXT)")
    song_id = start

    for song in data:

        song_id = song_id + 1
        ranking = song['ranking']
        country = song['country']
        title = song['title']
        artist = song['artist']
        
        cur.execute("INSERT OR IGNORE INTO Discogs (song_id, ranking, country, title, artist) VALUES (?, ?, ?, ?, ?)", (song_id, ranking, country, title, artist))

    conn.commit()

if __name__ == '__main__':
    cur, conn = setUpDatabase('music.db')

    top_25_US_discogs = get_discog_songs('US')
    top_25_FR_discogs = get_discog_songs('France')
    top_25_CA_discogs = get_discog_songs('Canada')
    top_25_UK_discogs = get_discog_songs('UK')

    set_up_discogs_table(top_25_US_discogs, 0, cur, conn)
    set_up_discogs_table(top_25_FR_discogs, 25, cur, conn)
    set_up_discogs_table(top_25_CA_discogs, 50, cur, conn)
    set_up_discogs_table(top_25_UK_discogs, 75, cur, conn)