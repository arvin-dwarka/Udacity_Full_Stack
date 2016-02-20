# Tournament Results

This project consists of a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament. The latter tournament uses the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

#### Description

**tournament.sql**: Defines DB schema which consists of TABLES, VIEW and a UNIQUE INDEX.

- TABLES (players, matches) to store data from the user.
- VIEWS (player_records) to simplify queries from the python script.
- UNIQUE INDEX (matches_unique) to prevent rematches between to players.

**tournament.py**: Python module consisting of functions that use tournament.sql database. This file uses the psycopg2 driver to use the PostgreSQL db.

***tournament_test.py***: Unit testing script that test functions from tournament.py.

#### How to run

You'll need a [Vagrant](www.vagrantup.com) container to run this module once you've downloaded this repo. Execute the following commands in terminal to spin up the virtual maching:

```
vagrant up
vagrant ssh
cd /vagrant/tournament
```

Then enter into `psql` to setup the database `tournament` with the following command:
```
\i tournament.sql
```

To run the unit tests on the python script, exit out of `psql` and execute the following command:
```
python tournament_test.py
```

Note: The Vagrant container will spin up a virtual machine as well as a `tournament` database from the schema defined in `tournament.sql` and will delete any previous `tournament` database.