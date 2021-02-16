from argparse import Action, ArgumentError


def extract_range(range_str: str) -> list:
    result = []
    for part in range_str.split(','):
        if '-' in part:
            a, b = part.split('-')
            result.extend(range(int(a), int(b) + 1))
        elif "+" in part:
            numbers = part.split("+")
            for num in numbers:
                result.append(int(num))
        else:
            result.append(int(part))
    return result


class RangeAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            video_range = extract_range(values)
        except ValueError:
            raise ArgumentError(self, "The video range parameter cannot be parsed")
        setattr(namespace, self.dest, video_range)
