import argparse
import os

import requests
from dotenv import load_dotenv

from exceptions import fetch_from_api
from src.Actions.RangeAction import RangeAction
from src.Actions.YoutubeURLAction import YoutubeURLAction
from src.Logger.Logger import Logger

# read dotenv-file
load_dotenv()
api_token: str = str(os.getenv("YOUTUBE_API_KEY"))
google_api_base_url: str = str(os.getenv("YOUTUBE_API_ROUTE"))


def main():
    parser = argparse.ArgumentParser(description="Check how much time I waste on this playlist")

    parser.add_argument("-p", "--playlist", help="YouTube video playlist url", action=YoutubeURLAction, required=True)
    parser.add_argument("-r", "--range",
                        help="Video range to select (example: -r 1,3-5,7+9+10). If not set, all videos are selected",
                        action=RangeAction)

    args = parser.parse_args()

    logger = Logger()

    try:
        logger.success("How much time I waste on this playlist was started")

        video_ids = retrieve_video_ids(args.playlist)
        filtered_ids = filter_video_ids(video_ids, args.range)
        video_durations = retrieve_video_duration(filtered_ids)
        duration = parse_duration(video_durations)

        parsed_time = parse_seconds_to_formatted_length(duration)

        print()
        logger.success("Playlist Details:")
        logger.success(f" - Duration: {parsed_time} for {len(filtered_ids)} videos")
    except fetch_from_api.FetchFromApiException as detail:
        logger.error("Fetch Exception")
        logger.error(str(detail))


def retrieve_video_ids(playlist_id: str) -> list:
    query_params = {
        "key": api_token,
        "maxResults": 50,
        "part": "snippet,contentDetails,id,status",
        "playlistId": playlist_id,
    }
    url = f"{google_api_base_url}/playlistItems"
    response = requests.get(url, query_params)
    json_response = response.json()
    items = json_response["items"]

    total_results: int = json_response["pageInfo"]["totalResults"]
    results_per_page: int = json_response["pageInfo"]["resultsPerPage"]
    pages = total_results // results_per_page
    for page_number in range(pages):
        if page_number < total_results - 1:
            query_params["pageToken"] = json_response["nextPageToken"]
        else:
            break
        response = requests.get(url, query_params)
        items += response.json()["items"]

    json_response = response.json()
    if "error" in json_response:
        raise fetch_from_api.FetchFromApiException(json_response["error"]["message"])

    return items


def filter_video_ids(items: list, range_list: list) -> list:
    video_ids = []
    for index, item in enumerate(items):
        if range_list is not None and index not in range_list:
            continue
        if item["status"]["privacyStatus"] == "public":
            video_ids.append(item["contentDetails"]["videoId"])

    return video_ids


def retrieve_video_duration(video_ids: list) -> list:
    query_params = {
        "key": api_token,
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


if __name__ == "__main__":
    main()
