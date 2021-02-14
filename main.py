import os, sys, getopt, requests
from exceptions import invalid_argument, invalid_url, fetch_from_api
import urllib.parse as urlparse
from urllib.parse import parse_qs
from src.Logger.Logger import Logger
from dotenv import load_dotenv


# read dotenv-file
load_dotenv()
api_token: str = str(os.getenv("YOUTUBE_API_KEY"))
google_api_base_url: str = str(os.getenv("YOUTUBE_API_ROUTE"))


def main():
    try:
        error_logger = Logger()
        error_logger.success("How much time I waste on this playlist was started")

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
    except invalid_url.InvalidUrlException as detail:
        print("Invalid URL:")
        print(detail)
    except fetch_from_api.FetchFromApiException as detail:
        print("Fetch Exception")
        print(detail)


def extract_playlist_id(playlist_url: str) -> str:
    if "youtube" not in playlist_url:
        raise invalid_url.InvalidUrlException("No Youtube URL was passed")

    parsed_url = urlparse.urlparse(playlist_url)
    if "list" not in parse_qs(parsed_url.query):
        raise invalid_url.InvalidUrlException("Missing 'list' query parameter")

    playlist_id = parse_qs(parsed_url.query)["list"][0]

    return playlist_id


def retrieve_video_ids(playlist_id: str) -> list:
    query_params = {
        "key": api_token,
        "maxResults": 9999,
        "part": "snippet,contentDetails,id,status",
        "playlistId": playlist_id,
    }
    url = f"{google_api_base_url}/playlistItems"
    response = requests.get(url, query_params)

    if "error" in response.json():
        raise fetch_from_api.FetchFromApiException(response.json()["error"]["message"])

    items = response.json()["items"]
    video_ids = []
    for item in items:
        if item["status"]["privacyStatus"] == "public":
            video_ids.append(item["contentDetails"]["videoId"])

    return video_ids


def retrieve_video_duration(video_ids: list) -> list:
    query_params = {
        "key": api_token,
        "maxResults": 9999,
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


def parse_duration(video_durations: list) -> int:
    hours_in_seconds = 3600
    minutes_in_seconds = 60

    duration_in_seconds = 0
    for duration in video_durations:
        hours = 0
        minutes = 0
        seconds = 0
        duration_without_prefix = duration[2:]

        if "H" in duration_without_prefix:
            hours = extract_numbers(duration_without_prefix, "H")

        if "M" in duration_without_prefix:
            minutes = extract_numbers(duration_without_prefix, "M")

        if "S" in duration_without_prefix:
            seconds = extract_numbers(duration_without_prefix, "S")

        duration_in_seconds += (int(hours) * hours_in_seconds) + (int(minutes) * minutes_in_seconds) + int(seconds)
    return duration_in_seconds


def extract_numbers(duration: str, time_unit) -> int:
    time_index = duration.index(time_unit) - 1
    current_val = duration[time_index]

    length = 1
    while is_integer(current_val) and time_index > 0:
        time_index -= 1
        length += 1

        if is_integer(duration[time_index:time_index + length]):
            current_val = duration[time_index:time_index + length]

    return int(current_val)


def is_integer(val) -> bool:
    try:
        _ = int(val)
    except ValueError:
        return False
    else:
        return True


def parse_seconds_to_formatted_length(duration: int) -> str:
    days = duration // 86400
    hours = (duration - (days * 86400)) // 3600
    minutes = (duration - ((hours * 3600) + (days * 86400))) // 60
    seconds = duration - ((days * 86400) + (hours * 3600) + (minutes * 60))

    return f"{days} days, {hours} hours, {minutes} minutes and {seconds} seconds"


def extract_url(parameters: list) -> str:
    opts, rest = getopt.getopt(parameters[1:], "p:", ["playlist:"])
    for key, val in opts:
        if key == "-p":
            return val
    raise invalid_argument.InvalidArgumentException()


if __name__ == "__main__":
    main()
