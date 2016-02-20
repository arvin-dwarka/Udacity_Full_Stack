#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def updateDatabase(*args):
    """Helper function that connects to the database, gets a cursor, execute 
    the update commands, and then commits the changes and closes the 
    connection."""
    db = connect()
    c = db.cursor()
    c.execute(*args)
    db.commit()
    db.close()


def queryDatabase(*args):
    """Helper function that connects to the database, gets a cursor, execute 
    the query command (cmd), and then commits the changes and closes the 
    connection."""
    db = connect()
    c = db.cursor()
    c.execute(*args)
    query = c.fetchall()
    db.close()
    return query


def deleteMatches():
    """Remove all the match records from the database."""
    updateDatabase('DELETE FROM matches;')


def deletePlayers():
    """Remove all the player records from the database."""
    updateDatabase('DELETE FROM players;')


def countPlayers():
    """Returns the number of players currently registered."""
    return queryDatabase('SELECT COUNT(*) FROM players;')[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    updateDatabase('INSERT INTO players (name) VALUES (%s);', (name,))


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    query = r'''SELECT players.id, players.name, player_records.wins, 
                        (player_records.wins + player_records.losses) AS sum
                FROM players NATURAL JOIN player_records
                ORDER BY player_records.wins DESC;'''

    return queryDatabase(query)


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    updateDatabase('INSERT INTO matches(winner, loser) VALUES (%s, %s);', (winner, loser))
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # query the player standings to get the current list of entries
    entry = [(player[0], player[1]) for player in playerStandings()]

    # pair each player with an adjescent player from the entry list
    return [(entry[i][0], entry[i][1], entry[i+1][0], entry[i+1][1]) 
        for i in xrange(0, len(entry), 2)]

