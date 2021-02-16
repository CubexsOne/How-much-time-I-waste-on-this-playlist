# How much time I waste on this playlist
## A simple application to check the length of a playlist

### Usage:
- Add youtube credentials to use the youtube API
  - in Code or
  - use "API_TOKEN"-environment variable
- Execute script with -p or --playlist and the full url of the playlist
- Wait for the result

### Full usage:
```bash
usage: main.py [-h] -p PLAYLIST [-r RANGE]

Check how much time I waste on this playlist

optional arguments:
  -h, --help            show this help message and exit
  -p PLAYLIST, --playlist PLAYLIST
                        YouTube video playlist url
  -r RANGE, --range RANGE
                        Video range to select (example: -r 1,3-5,7+9+10). If not set, all videos are selected
```

### Get Google API Token:
- Login on https://console.cloud.google.com/home/dashboard
- Create a project
- Navigate to "APIs & Services"
- Add "Youtube Data API" as library
- Navigate to "Credentials"
- Click "Create Credentials" -> API key
- Copy Token and use the token direct in the Code or as "API_TOKEN" environment variable

---
Made with ❤️ by [CubexsOne](https://cubexs.dev/)