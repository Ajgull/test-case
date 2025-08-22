import re
import sys


def valid_urls(urls: list) -> list:
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})'
    )
    return [url for url in urls if url_pattern.fullmatch(url)]


def is_positive_int_value(value: int) -> bool:
    try:
        int_val = int(value)
        return int_val > 0
    except ValueError:
        print('Input count is not int or positive')
        return False


def load_hosts_from_file(filename: str) -> list:
    try:
        with open(filename, 'r', encoding='UTF-8') as file_in:
            lines = file_in.readlines()
            lines = [line.strip() for line in lines]
    except FileNotFoundError as e:
        print(f'Error while loading data from file {filename}')
        sys.exit(1)
    return lines


def load_statistics_to_file(filename: str, data: str) -> None:
    try:
        with open(filename, 'w', encoding='UTF-8') as file_out:
            file_out.write(data)
    except IOError:
        print(f'Output error when working with a {filename}')
    except Exception as e:
        print(f'Error of work with file, {str(e)}')
        sys.exit(1)


def format_statistics(data: list) -> str:
    lines = []
    for item in data:
        lines.append(f"  Host: {item['Host']}")
        lines.append(f"  Successes: {item['Success']}")
        lines.append(f"  Failed: {item['Failed']}")
        lines.append(f"  Errors: {item['Errors']}")
        lines.append(f"  Min: {item['Min']} ms")
        lines.append(f"  Max: {item['Max']} ms")
        lines.append(f"  Avg: {item['Avg']} ms")
        lines.append('=' * 40)
    return '\n'.join(lines)