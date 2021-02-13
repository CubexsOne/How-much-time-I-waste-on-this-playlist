from exceptions import invalid_argument
import os
import sys
import getopt
import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs


api_token = "Add your google API Token here"
if "API_TOKEN2" in os.environ:
    api_token = os.environ["API_TOKEN"]

google_api_base_url = "https://www.googleapis.com/youtube/v3"


def extract_playlist_id(playlist_url: str) -> str:
    parsed_url = urlparse.urlparse(playlist_url)
    playlist_id = parse_qs(parsed_url.query)["list"][0]

    return playlist_id


def retrieve_video_ids(playlist_id: str) -> list[str]:
    query_params = {
        "key": api_token,
        "maxResults": 25,
        "part": "snippet,contentDetails,id,status",
        "playlistId": playlist_id,
    }
    url = f"{google_api_base_url}/playlistItems"
    response = requests.get(url, query_params)

    items = response.json()["items"]
    video_ids = []
    for item in items:
        video_ids.append(item["contentDetails"]["videoId"])

    return video_ids


def retrieve_video_duration(video_ids: list[str]) -> list[str]:
    query_params = {
        "key": api_token,
        "maxResults": 25,
        "part": "contentDetails",
        "id": ""
    }

    url = f"{google_api_base_url}/videos"
    durations = []
    for video_id in video_ids:
        query_params["id"] = video_id
        response = requests.get(url, query_params)
        items = response.json()["items"]
        duration = items[0]["contentDetails"]["duration"]

        durations.append(duration)

    return durations


def parse_duration(video_durations: list[str]) -> int:
    hours_in_seconds = 3600
    minutes_in_seconds = 60

    duration_in_seconds = 0
    for duration in video_durations:
        duration_without_prefix = duration[2:]
        hours = duration_without_prefix.split("H")[0]

        duration_without_hours = duration[2:].split("H")[1]
        minutes = duration_without_hours.split("M")[0]

        duration_without_minutes = duration_without_hours.split("M")[1]
        seconds = duration_without_minutes.split("S")[0]

        duration_in_seconds += (int(hours) * hours_in_seconds) + (int(minutes) * minutes_in_seconds) + int(seconds)
    return duration_in_seconds


def parse_seconds_to_formatted_length(duration: int) -> str:

    hours = duration // 3600
    minutes = (duration - (hours * 3600)) // 60
    seconds = duration - ((hours * 3600) + (minutes * 60))

    return f"{hours}:{minutes}:{seconds}"


def main():
    try:
        playlist_url = extract_url(sys.argv)
        playlist_id = extract_playlist_id(playlist_url)

        video_ids = retrieve_video_ids(playlist_id)
        video_durations = retrieve_video_duration(video_ids)
        duration = parse_duration(video_durations)

        parsed_time = parse_seconds_to_formatted_length(duration)

        print("Playlist Details:")
        print(f" - Duration: {parsed_time}")
    except invalid_argument.InvalidArgumentException:
        print("Missing or invalid Arguments:")
        print("Usage:")
        print("-p or --playlist PlaylistURL")


def extract_url(parameters: list[str]) -> str:
    opts, rest = getopt.getopt(parameters[1:], "p:", ["playlist:"])
    for key, val in opts:
        if key == "-p":
            return val
    raise invalid_argument.InvalidArgumentException("This has no params")


if __name__ == "__main__":
    main()
