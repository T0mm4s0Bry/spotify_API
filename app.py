from flask import Flask, redirect, request, url_for, render_template,session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#le tue credenziali le trovi nella dashboard di prima
SPOTIFY_CLIENT_ID = "4a2cbb97c5504b7dbe7a2efc0c840bf2"
SPOTIFY_CLIENT_SECRET = "0fb3aa1797704da5925b662d34732f95"
SPOTIFY_REDIRECT_URI = "https://5000-t0mm4s0bry-spotifyapi-kost5ot2kr8.ws-eu117.gitpod.io/callback" #dopo il login andiamo qui

app = Flask(__name__)
app.secret_key = 'chiave_per_session'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-private playlist-read-private",
    show_dialog=True
)

@app.route('/')
def home():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_info = sp.current_user()
    playlists = sp.current_user_playlists()['items']
    
    playlist_id = request.args.get('playlist_id')
    tracks = []
    if playlist_id:
        tracks_data = sp.playlist_items(playlist_id)['items']
        tracks = [
            {
                'name': track['track']['name'],
                'artist': track['track']['artists'][0]['name'],
                'album': track['track']['album']['name'],
                'cover': track['track']['album']['images'][0]['url'] if track['track']['album']['images'] else None
            } 
            for track in tracks_data
        ]
    
    return render_template('home.html', user_info=user_info, playlists=playlists, tracks=tracks)

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)