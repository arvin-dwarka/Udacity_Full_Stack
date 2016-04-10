import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
  """User profile"""
  name = ndb.StringProperty(required=True)
  email = ndb.StringProperty(required=True)
  wins = ndb.IntegerProperty(default=0)
  total_played = ndb.IntegerProperty(default=0)

  @property
  def win_percentage(self):
    if self.total_played > 0:
      return float(self.wins)/float(self.total_played)
    else:
      return 0

  def to_form(self):
    return UserForm(name=self.name,
                    email=self.email,
                    wins=self.wins,
                    total_played=self.total_played,
                    win_percentage=self.win_percentage
                    )

  def add_win(self):
    self.wins += 1
    self.total_played += 1
    self.put()

  def add_loss(self):
    self.total_played += 1
    self.put()

class Game(ndb.Model):
  """Game object"""
  answer = ndb.PickleProperty(required=True)
  check_answer = ndb.PickleProperty()
  attempts_remaining = ndb.IntegerProperty(required=True, default=6)
  game_over = ndb.BooleanProperty(required=True, default=False)
  user = ndb.KeyProperty(required=True, kind='User')
  move_histories = ndb.PickleProperty()

  @classmethod
  def new_game(cls, user, answer, attempts):
    """Creates and returns a new game"""
    if attempts < 1:
      raise ValueError('Number of attempts has be greater than 1!')
    game = Game(user=user,
                attempts_remaining=attempts,
                game_over=False)
    game.answer = list(answer)
    game.check_answer = ['']*len(game.answer)
    game.move_histories = []
    game.put()
    return game

  def to_form(self, message):
    """Returns a GameForm representation of the Game"""
    form = GameForm()
    form.urlsafe_key = self.key.urlsafe()
    form.user_name = self.user.get().name
    form.attempts_remaining = self.attempts_remaining
    form.check_answer = self.check_answer
    form.game_over = self.game_over
    form.message = message
    return form

  def end_game(self, won=False):
    """Ends the game - if won is True, the player won. - if won is False,
    the player lost."""
    self.game_over = True
    self.put()
    # Add the game to the score 'board'
    score = Score(user=self.user, 
                  date=date.today(), 
                  won=won,
                  attempts_remaining=self.attempts_remaining, 
                  answer=self.answer
                  )
    score.put()


class Score(ndb.Model):
  """Score object"""
  user = ndb.KeyProperty(required=True, kind='User')
  date = ndb.DateProperty(required=True)
  won = ndb.BooleanProperty(required=True)
  attempts_remaining = ndb.IntegerProperty(required=True)
  answer = ndb.PickleProperty(required=True)

  def to_form(self):
    return ScoreForm(user_name=self.user.get().name, 
                      won=self.won,
                      date=str(self.date),
                      attempts_remaining=self.attempts_remaining
                      )


class UserForm(messages.Message):
  """User Form"""
  name = messages.StringField(1, required=True)
  email = messages.StringField(2, required=True)
  wins = messages.IntegerField(3, required=True)
  total_played = messages.IntegerField(4, required=True)
  win_percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):
  """Container for multiple User Forms"""
  items = messages.MessageField(UserForm, 1, repeated=True)


class GameForm(messages.Message):
  """GameForm for outbound game state information"""
  urlsafe_key = messages.StringField(1, required=True)
  attempts_remaining = messages.IntegerField(2, required=True)
  game_over = messages.BooleanField(3, required=True)
  message = messages.StringField(4, required=True)
  user_name = messages.StringField(5, required=True)


class GameForms(messages.Message):
  """Multiple GameForm container"""
  items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
  """Used to create a new game"""
  user_name = messages.StringField(1, required=True)
  answer = messages.StringField(2, required=True)
  attempts = messages.IntegerField(3, default=5)


class MakeMoveForm(messages.Message):
  """Used to make a move in an existing game"""
  user_name = messages.StringField(1, required=True)
  move = messages.StringField(2, required=True)


class GameHistory(messages.Message):
  """Game history"""
  move = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
  """ScoreForm for outbound Score information"""
  user_name = messages.StringField(1, required=True)
  date = messages.StringField(2, required=True)
  won = messages.BooleanField(3, required=True)
  attempts_remaining = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
  """Return multiple ScoreForms"""
  items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
  """StringMessage-- outbound (single) string message"""
  message = messages.StringField(1, required=True)

