from project import db
import enum
import datetime


class Game(db.Model):
    __tablaname__ = "game"
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_name = db.Column(db.String(80))
    players = db.relationship("User", back_populates="game")
    rounds = db.relationship("Round", back_populates="game")
    start_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    started = db.Column(db.Boolean, default=False)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    alive = db.Column(db.Boolean, default=True)
    type_player = db.Column(db.String(80))
    game_id = db.Column(db.ForeignKey('game.id'))
    game = db.relationship('Game', back_populates="players")

    __mapper_args__ = {'polymorphic_identity': 'villager',
                       'polymorphic_on': type_player}

    def __repr__(self):
        return '<User {name}>'.format(name=self.username)


class Wolf(User):
    __tablename__ = "wolf"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'wolf'}


class RoundType(enum.Enum):
    day = 0
    night = 1


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship('Game', back_populates="rounds")
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
