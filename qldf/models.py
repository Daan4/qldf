from qldf import db
from flask import flash
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, index=True)
    date_created = db.Column(db.DateTime, default=utcnow())
    date_modified = db.Column(db.DateTime, default=utcnow(), onupdate=utcnow())

    @classmethod
    def create(cls, success_msg=None, failure_msg=None, **kwargs):
        new_record = cls(**kwargs)
        try:
            db.session.add(new_record)
            db.session.commit()
            if success_msg:
                flash(success_msg)
        except (IntegrityError, InvalidRequestError):
            db.session.rollback()
            if failure_msg:
                flash(failure_msg)

    @classmethod
    def delete(cls, success_msg=None, unmapped_msg=None, failure_msg=None, **kwargs):
        existing_record = cls.query.filter_by(**kwargs).first()
        try:
            db.session.delete(existing_record)
            db.session.commit()
            if success_msg:
                flash(success_msg)
        except UnmappedInstanceError:
            db.session.rollback()
            if unmapped_msg:
                flash(unmapped_msg)
        except IntegrityError:
            db.session.rollback()
            if failure_msg:
                flash(failure_msg)


class Player(BaseModel):
    __tablename__ = 'player'
    name = db.Column(db.Text, nullable=False)
    steam_id = db.Column(db.Text, unique=True, nullable=False, index=True)
    records = db.relationship('Record', backref='player', lazy=True)
    avatar_url = db.Column(db.Text)

    def __repr__(self):
        return f'<Player {self.id}>'


class Record(BaseModel):
    __tablename__ = 'record'
    mode = db.Column(db.Integer, nullable=False)
    map_id = db.Column(db.Integer, db.ForeignKey('map.id'), index=True, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), index=True, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    match_guid = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Record {self.id}>'


class Map(BaseModel):
    __tablename__ = 'map'
    name = db.Column(db.Text, nullable=False, unique=True)
    records = db.relationship('Record', backref='map', lazy=True)
    workshop_item_id = db.Column(db.Integer, db.ForeignKey('workshop_item.id'), index=True)

    def __repr__(self):
        return f'<Map {self.id}>'


class WorkshopItem(BaseModel):
    __tablename__ = 'workshop_item'
    item_id = db.Column(db.Text, unique=True, nullable=False, index=True)
    name = db.Column(db.Text)
    author_steam_id = db.Column(db.Text)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    size = db.Column(db.Float)
    num_comments = db.Column(db.Integer)
    score = db.Column(db.Integer)
    num_scores = db.Column(db.Integer)
    preview_url = db.Column(db.Text)
    maps = db.relationship('Map', backref='workshop_item', lazy=True)

    def __repr__(self):
        return f'<WorkshopItem {self.id}>'


class Server(BaseModel):
    __tablename__ = 'server'
    server_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    address = db.Column(db.Text)
    country = db.Column(db.Text)
    map = db.Column(db.Text)
    max_players = db.Column(db.Integer)
    name = db.Column(db.Text)
    """ JSON blob with player information
    players format (1 dict per player):
    [{name: string, score: int, totalConnected:string}]
    """
    players = db.Column(db.Text)
    # comma delimited string with server tags
    keywords = db.Column(db.Text)

    def __repr__(self):
        return f'<Server {self.id}>'
