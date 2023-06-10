from moviepy.editor import VideoFileClip
import requests
import json


client_id = "Client_Id"

def get_access_token(id, is_vod):
    data = {
        "operationName": "PlaybackAccessToken",
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712"
            }
        },
        "variables": {
            "isLive": not is_vod,
            "login": "" if is_vod else id,
            "isVod": is_vod,
            "vodID": id if is_vod else "",
            "playerType": "embed"
        }
    }

    headers = {
        "Client-id": client_id
    }

    response = requests.post("https://gql.twitch.tv/gql", headers=headers, json=data)
    response.raise_for_status()
    json_data = response.json()

    if is_vod:
        return json_data["data"]["videoPlaybackAccessToken"]
    else:
        return json_data["data"]["streamPlaybackAccessToken"]

def get_playlist(id, access_token, is_vod):
    url = f"https://usher.ttvnw.net/{'vod' if is_vod else 'api/channel/hls'}/{id}.m3u8"
    params = {
        "client_id": client_id,
        "token": access_token["value"],
        "sig": access_token["signature"],
        "allow_source": "true",
        "allow_audio_only": "true"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.text

def parse_playlist(playlist):
    lines = playlist.split("\n")
    parsed_playlist = []
    for i in range(4, len(lines), 3):
        quality = lines[i - 2].split('NAME="')[1].split('"')[0]
        resolution = lines[i - 1].split("RESOLUTION=")[1].split(",")[0] if "RESOLUTION" in lines[i - 1] else None
        url = lines[i]
        parsed_playlist.append({"quality": quality, "resolution": resolution, "url": url})

    return parsed_playlist

def get_stream(channel):
    try:
        access_token = get_access_token(channel, False)
        playlist = get_playlist(channel, access_token, False)
        return parse_playlist(playlist)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def play_live_stream(url):
    video = VideoFileClip(url)
    video.preview()

# Example usage
channel_name = "Channel_Name"
stream = get_stream(channel_name)
if stream:
    stream_url = stream[0]["url"]
    play_live_stream(stream_url)
else:
    print("Error: Unable to retrieve stream information.")