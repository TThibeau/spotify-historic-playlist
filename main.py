from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth 

from login import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

import requests
import os
import pprint as pp

os.system("cls || clear")

def GetPlaylistID(username, playlist_name):
    playlist_id = ''
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:  # iterate through playlists I follow
        if playlist['name'] == playlist_name:  # filter for newly created playlist
            playlist_id = playlist['id']
    return playlist_id

# --------------- USER INPUT --------------- 
year = "2010-03-01"
response = requests.get(f"https://www.billboard.com/charts/hot-100/{year}/")
top100 = response.text
# year = input("Which date do you want to travel to? Type the date in this format YYYY-MM-DD: "

# --------------- MAKE LIST OF SONGS --------------- 
soup = BeautifulSoup(top100,'html.parser')
entries = [a.getText().strip() for a in soup.select(".a-no-trucate")]

songs = [entries[i] for i in range(0,len(entries),2)]
artist = [entries[i] for i in range(1,len(entries),2)]

# --------------- SPOTIFY AUTHENTICATION --------------- 
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-public",
        redirect_uri="http://example.com",
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# --------------- FOR EACH SONG, FIND THE URI ---------------
sp_artist_uri = []
sp_track_uri = []

for r in range(len(songs)):
    result = sp.search(q='artist:' +artist[r],type='artist')
    sp_artist_uri.append(result['artists']['items'][0]['uri'])
    sp_artist_tracks = sp.artist_top_tracks(sp_artist_uri[r])   # NOTE: This does not cover all songs for the artist.
    for track in sp_artist_tracks['tracks']:
        if track['name'] == songs[r]:
            sp_track_uri.append(track['uri'])

# ---------------  MAKE A PLAYLIST ---------------  
playlist_name = f"Time travel to {year}"

playlist_id = GetPlaylistID(username=user_id,playlist_name=playlist_name)

if playlist_id == "":   # Playlist does not (yet) exist
    print(f"Creating a new playlist: {playlist_name}")
    sp.user_playlist_create(user_id, name=playlist_name)
    playlist_id = GetPlaylistID(username=user_id,playlist_name=playlist_name)

# ---------------  FIND SONGS ALREADY IN PLAYLIST ---------------  
else: 
    result = sp.user_playlist_tracks(user=user_id,playlist_id=playlist_id)['items']
    track_uris_playlist = [i['track']['uri'] for i in result]

    for uri in track_uris_playlist:
        if uri in sp_track_uri:
            sp_track_uri.remove(uri)

# ---------------  ADD SONGS TO PLAYLIST ---------------  
if sp_track_uri:
    results = sp.user_playlist_add_tracks(user_id, playlist_id, sp_track_uri)
    print("The songs have been added to the playlist ;)")
else:
    print("The songs were already part of the playlist")