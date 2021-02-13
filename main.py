from exceptions import invalid_argument
import sys
import getopt


def main():
    try:
        playlist_url = extract_url(sys.argv)
        print(f"PlaylistURL: {playlist_url}")
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
