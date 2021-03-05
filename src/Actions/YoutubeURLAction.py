from argparse import Action, ArgumentError
from urllib.parse import urlparse, parse_qs


class YoutubeURLAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):

        url = urlparse(values)
        if "youtube" not in url.netloc:
            raise ArgumentError("No Youtube URL was passed")

        query_params = parse_qs(url.query)
        if "list" not in query_params:
            raise ArgumentError("Missing 'list' query parameter")

        setattr(namespace, self.dest, query_params["list"][0])
