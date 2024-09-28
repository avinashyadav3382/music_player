from flask import Flask,current_app as app, render_template, request, redirect, url_for, flash, Blueprint, abort
from application.model import *
from sqlalchemy.exc import SQLAlchemyError
import os
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps




def roles_required(*required_roles):
    def wrapper(view_func):
        @wraps(view_func)
        def decorated_view(*args, **kwargs):
            if not (current_user.role in required_roles):
                abort(403)  # Forbidden
            return view_func(*args, **kwargs)
        return decorated_view
    return wrapper

#my routes are as follows
# / for index page
# /about for about page
# /signup for signup page
# /login for login page
# /logout for logout page
# /admin for admin dashboard
# /admin/user_management for user management
# /admin/all_users for all users
# /admin/all_creators for all creators
# /admin/all_albums for all albums
# /admin/promote_user/<int:user_id> for promoting user to creator
# /admin/demote_user/<int:user_id> for demoting creator to user
# /admin/user_management/block/<int:user_id> for blocking user
# /admin/user_management/unblock/<int:user_id> for unblocking user
# /admin/song/<int:song_id> for playing song
# /admin/album/<int:album_id> for playing album
# /admin/all_songs for all songs
# /admin/search for searching
# /admin/song/delete/<int:song_id> for deleting song
# /admin/search for searching
# /creator/dashboard for creator dashboard
# /creator/switch_to_user for switching to user
# /creator/album for creator album
# /creator/album/create_new for creating new album
# /creator/song for creator song
# /creator/song/create_new for creating new song
# /creator/song/delete/<int:song_id> for deleting song
# /creator/song/edit/<int:song_id> for editing song
# /creator/song/<int:song_id> for playing song
# /creator/album/<int:album_id> for playing album
# /creator/search for searching
# /user/dashboard for user dashboard
# /user_profile for user profile
# /user_profile/edit for editing user profile
# /user/all_albums for all albums
# /user/all_songs for all songs
# /user/song/<int:song_id> for playing song
# /user/register_creator for registering as creator
# /rate_song/<int:song_id> for rating song




#====================================== Normal Route Starting ======================================================

@app.route('/')
def index():
    return redirect(url_for("login"))
    

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("logged_out/about.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("logged_out/signup.html")

    elif request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        #checking if any field is left blank or not
        if password=="" or email=="" or username=="":
            flash("important fields can't be empty.....kindly fill details", "error")
            return redirect(url_for("signup"))
        
        #check if username already exist
        existing_user_username = User.query.filter_by(username=username).first()
        if existing_user_username:
            flash("Username already exist...Choose diffrent one", "error")
            return redirect(url_for("signup"))
        
        #if all test passed, add it in User table 
        new_user = User(name=name, email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account Created successfully....please login", "success")
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("logged_out/login.html")

    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username=="" or password=="":
            flash("kindly enter username or password, these can't be blank....")
            return redirect(url_for("login"))


        #fetching details of username
        user = User.query.filter_by(username=username).first()
        
        #checking if user exist or not
        if user:
            if user.user_status == "blocked":
                flash("your accound is blocked....contact admin   admin@admin.com")
                return redirect(url_for("login"))
            elif user.check_password(password):  #checking password
                if user.role == "creator":
                    flash(f"Welcome to Music World{user.name}")
                    login_user(user)
                    return redirect(url_for("creator_dashboard"))

                elif user.role == "user":
                    flash ("normal user login", "success")
                    flash(f"Welcome to Music World {user.name}")
                    login_user(user)
                    return redirect(url_for("dashboard"))
                
                else:
                    flash("If You are admin.... login here", "error")
                    return redirect(url_for("admin_login"))
                
            
            else:
                flash("check passwords", "error")
                return redirect(url_for("login"))
        else:
            flash("username does not exist", "error")
            return redirect(url_for("login"))


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("logged_out/admin_login.html")

    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username=="" or password=="":
            flash("kindly enter username or password, these can't be blank....")
            return redirect(url_for("admin_login"))


        #fetching details of username
        user = User.query.filter_by(username=username, role="admin").first()
        
        #checking if user exist or not
        if user:
            if user.user_status == "blocked":
                flash("your accound is blocked....contact admin   admin@admin.com")
                return redirect(url_for("admin_login"))
            elif user.check_password(password):  #checking password
                if user.role=="admin":
                    flash("Welcome Admin")
                    login_user(user)
                    return redirect(url_for("admin"))
                
                else:
                    flash("You are not admin.... login as normal user")
                    return redirect(url_for("login"))
                
                
            else:
                flash("check passwords", "error")
                return redirect(url_for("admin_login"))
        else:
            flash("username does not exist", "error")
            return redirect(url_for("admin_login"))

    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("logout successfully" , "logout")
    return redirect(url_for("login"))

#====================================== Normal Route Ending ======================================================




#====================================== Admin Route Starting ======================================================

@app.route("/admin")
@login_required
def admin():
    try:
        #total_user=User.query.count()
        total_user = User.query.filter_by(role="user").count()
        total_creator = User.query.filter_by(role="creator").count()
        total_album = Album.query.count()
        total_songs= Song.query.count()
        total_playlist = Playlist.query.count()
        trending_songs = Song.query.order_by(Song.average_rating.desc()).limit(10).all()
        return render_template("admin/dashboard.html", total_user=total_user, total_creator=total_creator, total_album=total_album, total_songs=total_songs, total_playlist = total_playlist, trending_songs=trending_songs)

    except SQLAlchemyError as e:
        # Handle database-related errors (e.g., connection issues)
        flash("An error occurred while fetching data from the database.", "error")
        return render_template("admin/error.html")
    


@app.route('/admin/user_management', methods=['GET'])
@login_required
@roles_required("admin")
def user_management():
    # Fetch a list of users from the database
    users = User.query.all()
    return render_template('admin/user_management.html', users=users)


@app.route("/admin/all_users")
@login_required
@roles_required('admin')  
def all_users():
    users = User.query.filter_by(role="user").all()
    return render_template("admin/all_users.html", users=users)

@app.route("/admin/all_creators")
@login_required
@roles_required('admin')  
def all_creators():
    users = User.query.filter_by(role="creator").all()
    return render_template("admin/all_users.html", users=users)

@app.route("/admin/all_albums")
@login_required
@roles_required('admin')  
def all_albums():
    albums = Album.query.all()
    songs = Song.query.all()
    return render_template("admin/all_albums.html", albums=albums, songs=songs)



@app.route('/admin/promote_user/<int:user_id>', methods=['GET'])
@login_required
@roles_required('admin')  
def promote_user(user_id):
    # Implement logic to promote the user with user_id to a creator role
    # Update the user's role in the database
    user = User.query.get(user_id)
    user.role = 'creator'
    db.session.commit()
    return redirect(request.referrer or  url_for('user_management'))

@app.route('/admin/demote_user/<int:user_id>', methods=['GET'])
@login_required
@roles_required('admin')  
def demote_user(user_id):
    # Implement logic to demote the user with user_id to a regular user role
    # Update the user's role in the database
    user = User.query.get(user_id)
    user.role = 'user'
    db.session.commit()
    return redirect(request.referrer or  url_for('user_management'))

@app.route("/admin/user_management/block/<int:user_id>", methods=["GET"])
@login_required
@roles_required('admin')  
def block_user(user_id):
    user = User.query.get(user_id)
    user.user_status = 'blocked'
    db.session.commit()
    return redirect(request.referrer or  url_for('user_management'))

    
# Define the unblock_user route
@app.route("/admin/user_management/unblock/<int:user_id>", methods=["GET"])
@login_required
@roles_required('admin')  
def unblock_user(user_id):
    user = User.query.get(user_id)
    user.user_status = 'active'
    db.session.commit()
    return redirect(request.referrer or  url_for('user_management'))




@app.route("/admin/song/<int:song_id>")
@roles_required('admin')  
@login_required
def admin_play_song(song_id):
    song = Song.query.filter_by(id = song_id).first()
    album_name = song.album.name
    
    if song is None:
        flash("Song not found")
        return render_template("error.html", error_message="Song not found")

    
    songs_info = [{'name': song.file_name, 'duration': song.duration, 'file_path': f"/static/songs/{song.file_name}"}]
    # Pass data to the template
    return render_template("admin/play_song.html",album_name=album_name, songs_data_json={'songs_info': songs_info})


@app.route("/admin/album/<int:album_id>")
@login_required
@roles_required("admin")
def admin_play_album(album_id):
    album = Album.query.get(album_id)
    album_name = album.name

    if album is None:
        return render_template("error.html", error_message="Album not found")

    songs = Song.query.filter_by(album_id=album_id).all()
    if not songs:
        return render_template("error.html", error_message="No songs found for this album")
    
    songs_info = [{'name': song.file_name, 'duration': song.duration, 'file_path': f"/static/songs/{song.file_name}"} for song in songs]
    # Pass data to the template
    return render_template("admin/play_song.html", album_name=album_name, songs_data_json={'songs_info': songs_info})


@app.route("/admin/all_songs")
@login_required
@roles_required("admin")
def admin_all_songs():
    songs = Song.query.all()
    return render_template( "admin/admin_all_songs.html", songs=songs)


import requests
@app.route("/admin/song/delete/<int:song_id>", methods=["GET"])
@login_required
@roles_required("admin")
def admin_delete_song(song_id):
    # Make a request to your API to delete the song

    api_url = f"http://{request.host}/api/songs"
    response = requests.delete(api_url, json={'id': int(song_id)})


    if response.status_code == 204:
        # Song deleted successfully
        flash("Song deleted successfully")
    elif response.status_code == 404:
        # Song not found
        flash("Song not found")
    else:
        # Handle other status codes as needed
        flash(f"Error deleting song. Status Code: {response.status_code}")

    return redirect(url_for("admin_all_songs"))



@app.route("/admin/search", methods=["GET", "POST"])
@login_required
@roles_required('admin')
def search():
    if request.method=="GET":
        return render_template("admin/search_result.html")
    if request.method=="POST":
        search = request.form.get("search")
        songs = Song.query.filter(Song.name.like(f"%{search}%")).all()
        albums = Album.query.filter(Album.name.like(f"%{search}%")).all()

        playlists = Playlist.query.filter(Playlist.name.like(f"%{search}%")).all()

        users=User.query.filter(User.name.like(f"%{search}%") | User.username.like(f"%{search}%")).all()
        

        return render_template("admin/search_result.html", songs=songs, albums=albums, users = users, playlists=playlists)



#================================================= Admin Route Ending ======================================================



#================================================= Common Route  ======================================================

def delete_album_and_songs(album):
    try:
        # Delete associated songs and files
        songs = Song.query.filter_by(album_id=album.id).all()
        for song in songs:
            file_to_remove = f"{song.file_name}"
            file_path = os.path.join(app.root_path, "static", "songs", file_to_remove)
            
            try:
                os.remove(file_path)
                db.session.delete(song)
                console.log(f"File {file_path} removed successfully.")
            except FileNotFoundError:
                console.log(f"File {file_path} not found.")
                return render_template("error.html", error_message="File not found")
        
        # Delete the album
        db.session.delete(album)
        db.session.commit()
        flash("Album deleted successfully")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the album")
    finally:
        db.session.close()

#Route to delete album by admin and creator
@app.route("/album/delete/<int:album_id>", methods=["GET"])
@login_required
@roles_required("admin", "creator")
def delete_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        flash("Album not found")
        return redirect(request.referrer or url_for("all_albums"))

    if current_user.role == "admin":
        delete_album_and_songs(album)
        return redirect(request.referrer or url_for("all_albums"))

    elif current_user.role == "creator" and album.owner_id == current_user.id:
        delete_album_and_songs(album)
        return redirect(request.referrer or url_for("creator_album"))

    else:
        flash("You are not authorized to delete this album")
        return redirect(request.referrer or url_for("logout"))


@app.route("/song/info/<int:song_id>")
@login_required
@roles_required('admin', "creator", "user")  
def song_info(song_id):
    song = Song.query.get(song_id)
    if not song:
        flash("Song not found")
        return redirect(request.referrer or url_for("all_songs"))
    
    if current_user.role=="admin":
        return render_template("admin/song_info.html", song=song)

    elif current_user.role=="creator" :
        return render_template("creator/song_info.html", song=song)
    
    else:
        return render_template("user/song_info.html", song=song)

    return render_template("admin/song_info.html", song=song)


#================================================= Common Route Ending ======================================================



#================================================= Creator Route Starting ======================================================

@app.route(("/creator/dashboard"))
@login_required
@roles_required('creator')  
def creator_dashboard():
    owner_id=current_user.id
    song_count = Song.query.filter_by(owner_id=owner_id).count()
    album_count = Album.query.filter_by(owner_id=owner_id).count()
    trending_songs = Song.query.filter_by(owner_id=current_user.id).order_by(Song.average_rating.desc()).limit(10).all()
    return render_template("creator/dashboard.html", song_count=song_count, album_count=album_count, trending_songs=trending_songs)


@app.route("/creator/switch_to_user")
@login_required
@roles_required('creator')
def switch_to_user():
    user = current_user
    user.role = 'user'  # Change the role to 'creator'
    db.session.commit()  # Save the changes to the database
    flash("You are now a user......")
    return redirect(url_for("dashboard"))


@app.route("/creator/album")
@login_required
@roles_required('creator')  
def creator_album():
    owner_id=current_user.id
    albums = Album.query.filter_by(owner_id=owner_id).all()
    songs = Song.query.all()

    return render_template("creator/album.html" , albums=albums, songs=songs)


@app.route("/creator/album/create_new", methods=["GET","POST"])
@login_required
@roles_required('creator')  
def create_new_album():
    if request.method=="GET":
        user_id=current_user.id
        user = User.query.get(user_id)

        return render_template("creator/create_album.html")

    if request.method=="POST":
        owner_id=current_user.id
        name= request.form.get("album_name")
        genre= request.form.get("genre")
        artist= request.form.get("artist")
        new_album = Album(owner_id=owner_id, name=name, genre=genre, artist=artist)
        albums = Album.query.filter_by(owner_id=owner_id, name=name).all()
        if albums:
            flash("Album already exist of this name....choose diffrent name")
            return redirect(url_for("create_new_album"))
        db.session.add(new_album)
        db.session.commit()
        flash("Album Created Successfully")
        return redirect(url_for("creator_album"))


@app.route("/creator/song")
@roles_required('creator')  
@login_required
def creator_song():
    owner_id=current_user.id
    songs = Song.query.filter_by(owner_id=owner_id).all()
    return render_template("creator/song.html", songs=songs)




@app.route('/creator/song/create_new', methods=['GET', 'POST'])
@login_required
@roles_required('creator')  
def create_new_song():
    if request.method=="GET":
        user_id=current_user.id
        user = User.query.get(user_id)
        albums = Album.query.filter_by(owner_id=user_id).all()
        return render_template('creator/create_song.html', albums=albums)
    
    if request.method=="POST":
        from werkzeug.utils import secure_filename
        from datetime import datetime
        import os
        owner_id=current_user.id
        name= request.form.get("song_name")
        lyrics= request.form.get("lyrics")
        duration= request.form.get("duration")
        album_id= request.form.get("album_id")
        song_file = request.files.get('song_file')
        
        
        # Check if the file is allowed
        if song_file and '.' in song_file.filename:
            ext = song_file.filename.rsplit('.', 1)[1].lower()
            if ext not in app.config['UPLOAD_EXTENSIONS']:
                flash("Invalid file type")
                return redirect(request.referrer or url_for("create_new_song"))
            # Save the file to the uploads folder

            song_id = Song.query.count() + 1
            filename = secure_filename(str(song_id) + ".mp3")
            already_exist = Song.query.filter_by(name=name, album_id=album_id).first()
            if already_exist:
                flash("Song already exist of this name....choose diffrent name")
                return redirect(url_for("create_new_song"))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            song_file.save(file_path)

            new_song = Song(owner_id=owner_id, name=name, lyrics=lyrics, duration=duration, album_id=album_id,file_name = filename, file_path=file_path, date_created=datetime.now())
            db.session.add(new_song)
            db.session.commit()
            flash("Song Created Successfully")
            return redirect(url_for("creator_song"))
        else:
            flash("Please upload a song file")
            return redirect(url_for("create_new_song"))




@app.route("/creator/song/delete/<int:song_id>", methods=["GET"])
@login_required
@roles_required("creator")
def delete_song(song_id):
    # Make a request to your API to delete the song
    api_url = f"http://{request.host}/api/songs"
    response = requests.delete(api_url, json={'id': int(song_id)})

    if response.status_code == 204:
        # Song deleted successfully
        flash("Song deleted successfully")
    elif response.status_code == 404:
        # Song not found
        flash("Song not found")
    else:
        # Handle other status codes as needed
        flash(f"Error deleting song. Status Code: {response.status_code}")
    return redirect(url_for("creator_song"))



@app.route("/creator/song/edit/<int:song_id>", methods=["GET", "POST"])
@login_required
def edit_song(song_id):
    song = Song.query.get(song_id)
    user_id=current_user.id
    albums = Album.query.filter_by(owner_id=user_id).all()
    if request.method=="GET":
        return render_template("creator/edit_song.html", song=song, albums=albums)
    
    if request.method=="POST":
        try:
            song.album_id = request.form.get("album_id")
            song.name = request.form.get("song_name")
            song.lyrics = request.form.get("lyrics")
            song.duration = request.form.get("duration")
            db.session.commit()
            flash("Song edited successfully")
            return redirect(url_for("creator_song"))

        except SQLAlchemyError as e:
            # Handle database-related errors (e.g., connection issues)
            flash("An error occurred while fetching data from the database.", "error")
            return redirect(url_for("creator_song"))

    return render_template("creator/edit_song.html", song=song)



@app.route("/creator/song/<int:song_id>")
@roles_required('creator')  
@login_required
def creator_play_song(song_id):
    song = Song.query.filter_by(id = song_id).first()
    album_name = song.album.name
    
    if song is None:
        flash("Song not found")
        return render_template("error.html", error_message="Song not found")

    
    songs_info = [{'name': song.file_name, 'duration': song.duration, 'file_path': f"/static/songs/{song.file_name}"}]
    # Pass data to the template
    return render_template("creator/play_song.html",album_name=album_name, songs_data_json={'songs_info': songs_info})
    
        

# For playing songs from an album
@app.route("/creator/album/<int:album_id>")
@login_required
def creator_play_album(album_id):
    album = Album.query.get(album_id)
    album_name = album.name

    if album is None:
        return render_template("error.html", error_message="Album not found")

    songs = Song.query.filter_by(album_id=album_id).all()
    if not songs:
        return render_template("error.html", error_message="No songs found for this album")
    
    songs_info = [{'name': song.file_name, 'duration': song.duration, 'file_path': f"/static/songs/{song.file_name}"} for song in songs]
    # Pass data to the template
    return render_template("creator/play_song.html", album_name=album_name, songs_data_json={'songs_info': songs_info})



@app.route("/creator/search", methods=["GET", "POST"])
@login_required
@roles_required('creator')
def search_song_creator():
    if request.method=="GET":
        return render_template("creator/search_result.html")
    if request.method=="POST":
        search = request.form.get("search")
        songs = Song.query.filter(Song.name.like(f"%{search}%") | Song.lyrics.like(f"%{search}%")).all()
        albums = Album.query.filter(Album.name.like(f"%{search}%") | Album.genre.like(f"%{search}%") | Album.artist.like(f"%{search}%") ).all()
        
        return render_template("creator/search_result.html", songs=songs, albums=albums, search=search)
  

#================================================= Creator Route Ending ======================================================








#================================================= User Route Starting ======================================================


#User's Dashboard
@app.route("/user/dashboard")
@roles_required('user')  
@login_required
def dashboard():
    total_albums = Album.query.count()
    total_songs= Song.query.count()
    total_playlist = Playlist.query.filter_by(user_id=current_user.id).count()
    trending_songs = Song.query.order_by(Song.average_rating.desc()).limit(10).all()
    return render_template("user/dashboard.html" , total_albums=total_albums, total_songs=total_songs, total_playlist = total_playlist, trending_songs=trending_songs)


@app.route("/user_profile")
@login_required
@roles_required('user', 'creator', 'admin')  
def profile():
    user = current_user
    if user.role=="admin":
        return render_template("admin/profile.html", user=user)

    elif user.role=="creator" :
        return render_template("creator/profile.html", user=user)
    
    else:
        return render_template("user/profile.html", user=user)



@app.route("/user_profile/edit", methods=["GET", "POST"])
@login_required
@roles_required('user', 'creator', 'admin')  
def edit_profile():
    user = current_user
    if request.method=="GET":
        return render_template("edit_profile.html", user=user)

    if request.method=="POST":
        try:
            user.name = request.form.get("name")
            user.email = request.form.get("email")
            user.username = request.form.get("username")
            user.password = generate_password_hash(request.form.get("password"), method='scrypt')

            db.session.commit()
            flash("Profile edited successfully")
            return redirect(url_for("profile"))

        except SQLAlchemyError as e:
            # Handle database-related errors (e.g., connection issues)
            print(f"Database error: {e}")
            flash("An error occurred while fetching data from the database.", "error")
            return redirect(url_for("profile"))




#show all albums to user
@app.route("/user/all_albums")
@login_required
@roles_required('user')  
def all_albums_user():
    albums = Album.query.all()
    songs = Song.query.all()
    return render_template("user/all_albums.html", albums=albums, songs=songs)


#show all songs to user
@app.route("/user/all_songs")
@login_required
@roles_required('user')  
def all_song_user():
    songs = Song.query.all()
    return render_template("user/all_songs.html", songs=songs)



# For playing songs from an album
@app.route("/user/song/<int:song_id>")
@roles_required('user')  
@login_required
def user_play_song(song_id):
    song = Song.query.filter_by(id = song_id).first()
    album_name = song.album.name
    
    if song is None:
        flash("Song not found")
        return render_template("error.html", error_message="Song not found")

    
    songs_info = [{'name': song.file_name, 'duration': song.duration, 'file_path': f"/static/songs/{song.file_name}"}]
    # Pass data to the template
    return render_template("user/play_song.html",album_name=album_name, songs_data_json={'songs_info': songs_info})
    

#change role of user to creator
@app.route("/user/register_creator")
@login_required
@roles_required('user')  
def register_creator():
    user = current_user
    user.role = 'creator'  # Change the role to 'creator'
    db.session.commit()  # Save the changes to the database
    flash("You are now a creator......")
    return redirect(url_for("creator_dashboard"))



@app.route("/rate_song/<int:song_id>", methods=["GET", "POST"])
@login_required
def rate_song(song_id):
    from sqlalchemy import func
    song = Song.query.get(song_id)
    
    if request.method == "GET":
        # Render the template with the song details and average rating
        average_rating = Rating.query.filter_by(song_id=song_id).with_entities(func.avg(Rating.individual_rating)).scalar()
        return render_template("user/rate_song.html", song=song, average_rating=average_rating)

    if request.method == "POST":
        # Handle the submitted rating
        individual_rating = int(request.form.get("rating"))

        # Store the individual rating in the Rating table
        already_rated = Rating.query.filter_by(user_id=current_user.id, song_id=song_id).first()
        if already_rated:
            already_rated.individual_rating = individual_rating
            db.session.commit()
            flash("Song rated successfully")
            return redirect(request.referrer or url_for("all_song_user"))
            flash("You have already rated this song")
            return redirect(request.referrer or url_for("all_song_user"))
            
        new_rating = Rating(user_id=current_user.id, song_id=song_id, individual_rating=individual_rating)
        db.session.add(new_rating)
        db.session.commit()

        # Calculate and update the average rating for the song
        average_rating = Rating.query.filter_by(song_id=song_id).with_entities(func.avg(Rating.individual_rating)).scalar()
        song.average_rating = round(average_rating, 2)  # Assuming you have an 'average_rating' column in the Song table
        db.session.commit()

        flash("Song rated successfully")
        return redirect(request.referrer or url_for("all_song_user"))



@app.template_filter('get_song_by_id')
def get_song_by_id(song_id):
    return Song.query.get(song_id)


@app.route("/user/all_playlist", methods=["GET", "POST"])
@login_required
@roles_required('user')
def user_all_playlist():
    if request.method == "GET":
        user_id = current_user.id
        playlists = Playlist.query.filter_by(user_id=user_id).all()
        songs = Song.query.all()
        
        return render_template("user/all_playlist.html", playlists=playlists, songs=songs)

    if request.method == "POST":
        playlist_name = request.form.get("playlist_name")
        user_id = current_user.id  # Fix here
        new_playlist = Playlist(name=playlist_name, user_id=user_id)
        db.session.add(new_playlist)
        db.session.commit()
        flash("Playlist created")
        return redirect(url_for("user_all_playlist"))



@app.route("/user/view_playlist/<int:playlist_id>")
@login_required
@roles_required('user')
def view_playlist(playlist_id):
    owner_name = current_user.name
    playlist = Playlist.query.get(playlist_id)
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).all()
    songs = []

    for playlist_song in playlist_songs:
        song = Song.query.get(playlist_song.song_id)
        songs.append(song)

    if not playlist or playlist.user_id != current_user.id:
        # Playlist not found or does not belong to the current user
        abort(404)

    songs_available = Song.query.all()  # Retrieve all songs
    
    return render_template("user/view_playlist.html", playlist=playlist, owner_name=owner_name, playlist_songs=playlist_songs, songs=songs, songs_available=songs_available)



@app.route("/user/play_playlist/<int:playlist_id>")
@login_required
@roles_required('user')
def play_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).all()
    songs = []

    for playlist_song in playlist_songs:
        song = Song.query.get(playlist_song.song_id)
        songs.append(song)

    if not playlist or playlist.user_id != current_user.id:
        # Playlist not found or does not belong to the current user
        abort(404)

    songs_info = [{'name': song.file_name, 'duration': song.duration, 'file_path': f"/static/songs/{song.file_name}"} for song in songs]
    # Pass data to the template
    return render_template("user/play_song.html", album_name=playlist.name, songs_data_json={'songs_info': songs_info})


@app.route("/user/delete_playlist/<int:playlist_id>", methods=["GET"])
@login_required
@roles_required('user')
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)

    if not playlist or playlist.user_id != current_user.id:
        # Playlist not found or does not belong to the current user
        abort(404)

    #delete songs associated to playlist form playlist_song table
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).all()
    for playlist_song in playlist_songs:
        db.session.delete(playlist_song)

    # Delete the playlist
    db.session.delete(playlist)

    db.session.commit()
    flash("Playlist deleted successfully")
    return redirect(url_for("user_all_playlist"))




@app.route("/user/manage_playlist/<int:playlist_id>", methods=["GET", "POST"])
@login_required
@roles_required('user')
def manage_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).all()
    songs = []

    for playlist_song in playlist_songs:
        song = Song.query.get(playlist_song.song_id)
        songs.append(song)

    if not playlist or playlist.user_id != current_user.id:
        # Playlist not found or does not belong to the current user
        abort(404)

    if request.method == "GET":
        songs_available = Song.query.all()  # Retrieve all songs
        return render_template("user/manage_playlist.html", playlist=playlist, playlist_songs=playlist_songs, songs=songs, songs_available=songs_available)
    
    if request.method == "POST":
        try:
            song_id = int(request.form.get("song_id"))
            
            # Check if the song is not already in the playlist
            if not PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first():
                playlist = Playlist.query.get(playlist_id)
                song = Song.query.get(song_id)

                if playlist and song:
                    playlist_song = PlaylistSong(playlist_id=playlist.id, song_id=song.id)
                    db.session.add(playlist_song)
                    db.session.commit()
                    flash(f"Song '{song.name}' added to playlist '{playlist.name}'", "success")
                else:
                    flash("Invalid playlist or song", "error")
            else:
                flash("Song already exists in the playlist", "warning")

        except ValueError:
            flash("Invalid input for song position or ID", "error")

        return redirect(url_for("manage_playlist", playlist_id=playlist_id))




@app.route("/user/remove_from_playlist/<int:playlist_id>/<int:song_id>", methods=["GET"])
@login_required
@roles_required('user')
def remove_from_playlist(playlist_id, song_id):
    playlist = Playlist.query.get(playlist_id)
    playlist_song = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()

    if not playlist or playlist.user_id != current_user.id:
        # Playlist not found or does not belong to the current user
        abort(404)

    if playlist_song:
        db.session.delete(playlist_song)
        db.session.commit()
        flash("Song removed from playlist successfully")
    else:
        flash("Song not found in playlist", "error")

    return redirect(url_for("manage_playlist", playlist_id=playlist_id))  







@app.route("/user/search", methods=["GET", "POST"])
@login_required
@roles_required('user')
def search_song_user():
    if request.method=="GET":
        return render_template("user/search_result.html")
    if request.method=="POST":
        search = request.form.get("search")
        songs = Song.query.filter(Song.name.like(f"%{search}%") | Song.lyrics.like(f"%{search}%")).all()
        albums = Album.query.filter(Album.name.like(f"%{search}%") | Album.genre.like(f"%{search}%") | Album.artist.like(f"%{search}%") ).all()
        playlists = Playlist.query.filter((Playlist.user_id == current_user.id) & Playlist.name.like(f"%{search}%")).all()

        return render_template("user/search_result.html", songs=songs, albums=albums,  playlists=playlists, search=search)




