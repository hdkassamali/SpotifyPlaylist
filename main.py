from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

date = input("What year would you like to travel to? Type the date in this format YYYY-MM-DD: ")
top_100_url = f"https://www.billboard.com/charts/hot-100/{date}/"

response = requests.get(top_100_url)
top_100_data = response.text

soup = BeautifulSoup(top_100_data, "html.parser")

songs_name = soup.select(selector="li h3", class_="c-title")

songs_list = []
for song in songs_name:
  song_text = song.get_text().strip()
  songs_list.append(song_text)
  if len(songs_list) > 99:
    break

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                          client_id=SPOTIFY_CLIENT_ID,
                          client_secret=SPOTIFY_CLIENT_SECRET,
                          redirect_uri=SPOTIFY_REDIRECT_URI,
                          scope="user-library-read playlist-modify-private",
                          cache_path="token.txt",
                          show_dialog=False))

user_id = sp.current_user()["id"]

song_uris = []
year = date.split("-")[0]

for song in songs_list:
  result = sp.search(q=f"track:{song} year: {year}", type="track")
  try:
    uri = result["tracks"]["items"][0]["uri"]
    song_uris.append(uri)
  except IndexError:
    print(f"{song} doesn't exist in spotify. Skipped")

spotify_playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
result = sp.playlist_add_items(playlist_id=spotify_playlist["id"], items=song_uris)
print(spotify_playlist)
