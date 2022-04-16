try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ModuleNotFoundError:
    print("Please install spotipy: pip install spotipy")
    exit()

"""Instructions: Make sure you have a Spotify account and have created a Spotify app.
    Go to https://developer.spotify.com/my-applications/
    Create a new app.
    Fill in the details below.
    Replace the client_id, client_secret, redirect_uri, and scope with your own.
    Save the file.
    Run the script.
"""

client_id = ""
client_secret = ""
redirect_uri = ""

if not client_id:
    client_id = input("Enter your client ID: ")
if not client_secret:
    client_secret = input("Enter your client secret: ")
if not redirect_uri:
    redirect_uri = input("Enter your redirect URI: ")

scope = "user-library-read,user-library-modify,playlist-modify-private," \
        "playlist-read-private,playlist-modify-public,playlist-read-collaborative"

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope,
                                                    redirect_uri=redirect_uri, cache_path=".cache"))


def get_fav_tracks():
    result = spotify.current_user_saved_tracks()
    tracks = result["items"]
    while result["next"]:
        result = spotify.next(result)
        tracks.extend(result["items"])
    return tracks


def get_playlist_track_uris(playlist_id):
    
    uri_list = []
    results = spotify.playlist_items(playlist_id, limit=100)
    tracks = results["items"]
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])
    for track in tracks:
        uri_list.append(track["track"]["uri"])
    return uri_list


def get_track_uri(track):
    return track["track"]["uri"]


def divide_chunks(list, n):
    for i in range(0, len(list), n):
        yield list[i:i + n]


new_playlist_id = input("Enter the Playlist URL to add to: ").split("/")[-1].split("?")[0]
print("Playlist ID: " + new_playlist_id)

print("Fetching existing track data for playlist")
existing_tracks = get_playlist_track_uris(playlist_id=new_playlist_id)
chunked_existing_tracks = list(divide_chunks(existing_tracks, 100))

# remove all tracks from playlist
print(f"Removing {len(existing_tracks)} tracks from playlist")
for i in range(len(chunked_existing_tracks)):
    print(f"\rPart {i + 1} of {len(chunked_existing_tracks)}", end="")
    spotify.playlist_remove_all_occurrences_of_items(playlist_id=new_playlist_id, items=chunked_existing_tracks[i])
print("\n")

# fetch favourite tracks
print("Getting Favourite tracks...")
tracks = get_fav_tracks()
tracks_to_add = list(divide_chunks([get_track_uri(track) for track in tracks], 100))

# add tracks to playlist
print("Adding tracks to playlist...")
for i in range(len(tracks_to_add)):
    print(f"\rPart {i + 1} of {len(tracks_to_add)}", end="")
    playlist_to_add = spotify.playlist_add_items(new_playlist_id, tracks_to_add[i])
print("\n")

print("Done!")
