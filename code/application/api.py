from flask_restful import Api, Resource, reqparse, abort
from flask import jsonify, flash, current_app as app
import os
from flask_restful import Api,Resource, fields, marshal_with, reqparse, abort
from application.model import *
from application.exception import NotFoundError



song_parser = reqparse.RequestParser()
song_parser.add_argument('id', type=int, required=True)

class SongsData(Resource):
    def get(self):
        songs = Song.query.all()
        song_list = [{'id': song.id, 'name': song.name} for song in songs]
        return jsonify(song_list)

    def delete(self):
        args = song_parser.parse_args()
        song_id = args['id']

        song = Song.query.get(song_id)
        if not song:
            abort(404, message='Song not found')

        # Delete related records
        self._delete_related_records(song)

        # Delete the song from the database
        db.session.delete(song)
        db.session.commit()

        # Delete the associated file
        file_name = f"{song_id}.mp3"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

        try:
            os.remove(file_path)
            flash("Song deleted successfully")
            return {'message': 'Song deleted successfully'}, 204
        except FileNotFoundError:
            abort(404, message='File not found')
        except Exception as e:
            abort(500, message=f"An error occurred: {e}")

    def _delete_related_records(self, song):
        # Delete related records
        Rating.query.filter_by(song_id=song.id).delete()
        PlaylistSong.query.filter_by(song_id=song.id).delete()


class AlbumsData(Resource):
    def get(self):
        albums = Album.query.all()
        album_list = [{'id': album.id, 'name': album.name} for album in albums]
        return jsonify(album_list)
    def delete(self):
        args = song_parser.parse_args()
        album_id = args['id']

        album = Album.query.get(album_id)
        if not album:
            abort(404, message='Album not found')

        # Delete related records
        songs = Song.query.filter_by(album_id=album_id).all()
        for song in songs:
            SongsData()._delete_related_records(song)
            db.session.delete(song)

        db.session.delete(album)
        db.session.commit()

        return {'message': 'Album deleted successfully'}, 204
