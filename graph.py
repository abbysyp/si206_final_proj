import matplotlib.pyplot as plt
import numpy as np
import os
import sqlite3
import unittest

def create_vis(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM Averages')
    records = cur.fetchall()
    ranking_avg_features = []
    for row in records:
        row_dict = {}
        ranking = row[0]
        avg_tempo = row[1]
        avg_danceability = row[2]
        avg_speechiness = row[3]
        avg_liveness = row[4]
        avg_loudness = row[5]
        row_dict['ranking'] = ranking
        row_dict['avg_tempo'] = avg_tempo
        row_dict['avg_danceability'] = avg_danceability
        row_dict['avg_speechiness'] = avg_speechiness
        row_dict['avg_liveness'] = avg_liveness
        row_dict['avg_loudness'] = avg_loudness
        ranking_avg_features.append(row_dict)
        
    return ranking_avg_features

def create_tempo_graph(lst):
    '''creating graph 1'''
    fig, ax1 = plt.subplots()
    x1 = []
    for rank in lst:
        x1.append(rank['ranking'])
    y1 = []
    for rank in lst:
        y1.append(rank['avg_tempo'])

    plt.scatter(x1, y1, c = "blue")
    plt.xticks(np.arange(0, len(x1) + 1, 1))
    

    plt.xlabel("Ranking")
    plt.ylabel("Average Tempo")

    plt.show()

def create_danceability_graph(lst):
    '''creating graph 2'''
    fig, ax = plt.subplots()

    rankings = []
    danceability_vals = []

    for item in lst:
        rankings.append(item['ranking'])
        danceability_vals.append(item['avg_danceability'])

    ax.plot(rankings, danceability_vals, 'm-', marker='o')

    ax.set(xlabel='rankings', ylabel='average danceability rating', title='average danceability for top 25 songs across Discogs and Deezer')
    
    ax.grid()

    plt.show()

def create_speechiness_graph(lst):
    '''creating graph 3'''
    fig = plt.figure()

    rankings = []
    speechiness_vals = []

    for item in lst:
        rankings.append(item['ranking'])
        speechiness_vals.append(item['avg_speechiness'])

    ax = fig.add_subplot(111)

    ax.bar(rankings, speechiness_vals, color='black')

    ax.set(xlabel='rankings', ylabel='average speechiness rating', title='average speechiness for top 25 songs across Discogs and Deezer')
    
    ax.grid()

    plt.show()

       
    
def main():
    data_lst = create_vis('music.db')

    create_tempo_graph(data_lst)

    create_danceability_graph(data_lst)
    
    create_speechiness_graph(data_lst)

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)