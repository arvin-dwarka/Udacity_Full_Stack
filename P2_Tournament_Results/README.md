# Tournament Results

This project consists of a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament. The latter tournament uses the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

#### How to run

You'll need a [Vagrant](www.vagrantup.com) container to run this module once you've downloaded this repo. Execute the following commands in terminal to run:

```
vagrant up
vagrant ssh
cd /vagrant/tournament
python tournament_test.py
```

Note: The Vagrant container will spin up a virtual machine as well as a `tournament` database from the schema defined in `tournament.sql`.