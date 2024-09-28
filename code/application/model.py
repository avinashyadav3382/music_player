from .database import db
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint, event




class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    user_status = db.Column(db.String, nullable=False, default="active")
    register_date = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String, nullable=False, default="user" )


    def __init__(self, name, email, username, password, role="user"):
        self.role = role
        self.name = name
        self.username = username
        self.email = email
        self.password = generate_password_hash(password, method='scrypt')

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    

class Album(db.Model):
    __tablename__ = "album"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    genre = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    owner_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False )
    songs_rel = relationship('Song', back_populates='album', lazy=True)
    



class Song(db.Model):
    __tablename__ = "song"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    lyrics = db.Column(db.String(), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    file_path = db.Column(db.String, nullable=False)
    file_name = db.Column(db.String, nullable=False)
    average_rating = db.Column(db.Float, default=0.0)

    album = relationship('Album', back_populates='songs_rel', lazy=True)

    __table_args__ = (UniqueConstraint('name', 'album_id'),)

def delete_songs_entries(mapper, connection, target):
    Rating.query.filter_by(song_id=target.id).delete()
    print("Deleted Ratings for Song")
    # Delete all PlaylistSong entries related to the deleted song
    PlaylistSong.query.filter_by(song_id=target.id).delete()
    print("Deleted PlaylistSong entries for Song")

# Attach the delete_playlist_songs function to the before_delete event of the Song class
event.listen(Song, 'before_delete', delete_songs_entries)    



class Rating(db.Model):
    __tablename__ = "rating"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    individual_rating = db.Column(db.Integer, nullable=False)

    # Add a unique constraint to ensure a user can rate a song only once
    __table_args__ = (db.UniqueConstraint('user_id', 'song_id'),)




class Playlist(db.Model):
    __tablename__ = "playlist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, default="New Playlist")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    playlist_songs = db.relationship('PlaylistSong', back_populates='playlist', lazy=True)

    

class PlaylistSong(db.Model):
    __tablename__ = "playlistsong"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)

    playlist = db.relationship('Playlist', back_populates='playlist_songs', lazy=True)
    song = db.relationship('Song', backref='playlist_songs')

    # Define a composite unique constraint to ensure songs are not repeated in the same playlist
    __table_args__ = (db.UniqueConstraint('playlist_id', 'song_id'),)

