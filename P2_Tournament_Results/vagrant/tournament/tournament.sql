-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- clear out old database to avoid any clash
DROP DATABASE IF EXISTS tournament;

-- create database for tournament
CREATE DATABASE tournament;

-- connect to tournament database
\c tournament;

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name varchar(225)
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    winner int REFERENCES players(id),
    loser int REFERENCES players(id)
);

-- create a player record view to get a count of their wins and losses
CREATE VIEW player_records AS
SELECT players.id,
    (CASE WHEN winning.times is NULL
     THEN 0 ELSE winning.times END) AS wins,
    (CASE WHEN losing.times is NULL
     THEN 0 ELSE losing.times END) AS losses
FROM players
    LEFT JOIN ( SELECT winner, COUNT(*) AS times
                FROM matches
                GROUP BY winner)
        AS winning
        ON players.id = winning.winner
    LEFT JOIN ( SELECT loser, COUNT(*) AS times
                FROM matches
                GROUP BY loser)
        AS losing
        ON players.id = losing.loser;

-- create unique pairing to prevent rematches from happening
CREATE UNIQUE INDEX matches_unique ON matches
  (greatest(winner, loser), least (winner, loser));