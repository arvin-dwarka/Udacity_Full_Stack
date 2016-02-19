#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def updateDatabse(*args):
    """Helper function that connects to the database, gets a cursor, execute 
    the update commands, and then commits the changes and closes the 
    connection."""
    db = connect()
    c = db.cursor()
    c.execute(*args)
    db.commit()
    db.close()


def queryDatabse(*args):
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
    updateDatabse('DELETE FROM Matches;')


def deletePlayers():
    """Remove all the player records from the database."""
    updateDatabse('DELETE FROM Players;')


def countPlayers():
    """Returns the number of players currently registered."""
    return queryDatabse('SELECT COUNT(*) FROM Players;')[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    updateDatabse('INSERT INTO Players (name) VALUES (%s);', (name,))


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
    # create sub query to calculate the number of wins and losses for use 
    # in main query as total mathces played
    sub_query = '''
    SELECT Players.id, Players.name, count({winner_or_loser}) as {wins_or_losses}
    FROM Players left join Matches
    ON Players.id = {winner_or_loser}
    GROUP BY Players.id
    '''
    
    # main query to return player standings sorted by wins
    main_query = '''
    SELECT Winners.id, Winners.name, Winners.wins, wins+losses as Played
    FROM ({winners}) as Winners LEFT JOIN ({losers}) as Losers
    ON Winners.id = Losers.id
    ORDER BY Winners.wins DESC;
    '''.format(
        winners=sub_query.format(
            winner_or_loser='winner',
            wins_or_losses='wins'
            ),
        losers=sub_query.format(
            winner_or_loser='loser',
            wins_or_losses='losses'
            )
        )
    return queryDatabse(main_query)


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    updateDatabse('INSERT INTO Matches VALUES (%s, %s);', (winner, loser))
 
 
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

