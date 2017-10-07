from project import db
import enum
import datetime


class Game(db.Model):
    __tablaname__ = "game"
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_name = db.Column(db.String(80))
    players = db.relationship("User", back_populates="game",
                              foreign_keys="[User.game_id]")
    rounds = db.relationship("Round", back_populates="game")
    start_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    started = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Game {name}>'.format(name=self.name)


class UserType(enum.Enum):
    villager = 0
    wolf = 1
    seer = 2
    hunter = 3
    cupid = 4
    witch = 5
    little_girl = 6


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    alive = db.Column(db.Boolean, default=True)
    type_player = db.Column(db.Enum(UserType))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship('Game', foreign_keys=[game_id],
                           back_populates="players")

    def __repr__(self):
        return '<User {name}>'.format(name=self.username)


class RoundType(enum.Enum):
    day = 0
    night = 1


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship('Game', foreign_keys=[game_id],
                           back_populates="rounds")
    round_type = db.Column(db.Enum(RoundType))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Round {game_id}>'.format(game_id=str(self.game_id))


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, primary_key=True)
    player_from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Vote {id}>'.format(id=str(self.id))
