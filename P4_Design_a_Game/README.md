# Design A Game - Hangman

## About

This project is a cloud-based API server of a Hangman game. The player needs to successfully attempt to guess the correct letters to a word answer to win.


## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application. 
 
 
## Game Description:
Hangman is a simple word guessing game. Each game begins with a random 'answer'
word, and a maximum number of 'attempts'. 'Attempts' are sent to the `make_move` endpoint which will reply
with either: 'correct', 'try again', 'you win', or 'game over' (if the maximum
number of attempts is reached).
Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

## Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 - settings.py: Web client ID for Google Cloud Platform

## Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, min, max, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Answers and attempts need to be longer than one letter.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, move
    - Returns: GameForm with new game state.
    - Description: Accepts a 'move' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created and the move history will be saved.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_user_games**
    - Path: '/user/{user_name}/games'
    - Method: GET
    - Parameters: user_name, email
    - Returns: StringMessage. 
    - Description: Returns all games recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **cancel_game**
    - Path: '/game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage. 
    - Description: Delete game record which provide by urlsafe_game_key
    Will raise a NotFoundException if the game does not exist.
    Will raise a BadRequestException if the game already over.

- **get_high_scores**
    - Path: '/high_wins'
    - Method: GET
    - Parameters: message_types.VoidMessage
    - Returns: UserForms
    - Description: Rank player based on the number of their wins.
    Will raise a NotFoundException if there is no user in the datastore.

- **get_user_ranking**
    - Path: '/get_user_ranking'
    - Method: GET
    - Parameters: message_types.VoidMessage
    - Returns: UserForms
    - Description: Rank player based on their win percentage.
    Will raise a NotFoundException if there is no user in the datastore.

- **get_game_history**
    - Path: '/game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: message_types.VoidMessage
    - Returns: GameHistory
    - Description: Return user's move history for the game with message and guess.
    Will raise a NotFoundException if there's no game matching the url safe key in the datastore.

## Models Included:
 - **User**
    - Stores unique user_name and email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
## Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **GameForms**
    - Multiple GameForm container.
 - **MakeMoveForm**
    - Inbound make move form (user_name, move).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    attempts_remaining).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **UserForm**
    - Representation of a User's state (name, email, wins, total_played, win_percentage)
 - **UserForms**
    - Multiple UserForm container.
 - **GameHistory**
    - Game moves container.