import argparse
import requests
import time
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed


def valid_urls(urls: list) -> list:
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})'
    )
    print([url for url in urls if url_pattern.fullmatch(url)])
    return [url for url in urls if url_pattern.fullmatch(url)]


def is_positive_int_value(value) -> bool:
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


def test_host(host: str, count: int) -> dict:
    success_count = 0
    fail_count = 0
    error_count = 0
    time_of_requests = []

    for i in range(count):
        try:
            start_time = time.time()
            response = requests.get(host, timeout=10)
            end_time = time.time()
            if 200 <= response.status_code < 400:
                success_count += 1
            else:
                fail_count += 1

            time_of_requests.append(round((end_time - start_time) * 1000, 3))

        except requests.HTTPError as e:
            print(f'Connection to host {host} {str(e)}')
            error_count += 1

    if time_of_requests:
        min_time = round(min(time_of_requests), 3)
        max_time = round(max(time_of_requests), 3)
        avg_time = round(sum(time_of_requests) / len(time_of_requests), 3)
    else:
        min_time = max_time = avg_time = 0

    return {
        'Host': host,
        'Success': success_count,
        'Failed': fail_count,
        'Errors': error_count,
        'Min': min_time,
        'Max': max_time,
        'Avg': avg_time
    }


def main():
    parallel_version = True

    parser = argparse.ArgumentParser(description="HTTP-server tester")

    parser.add_argument(
        "-H", "--hosts", required=False,
        help="Write the host"
    )
    parser.add_argument(
        "-C", "--count", type=int, default=1, required=True,
        help="Write count of requests"
    )
    parser.add_argument(
        "-F", "--file", type=str, required=False,
        help="Write name of in_file"
    )
    parser.add_argument(
        "-O", "--out", type=str, required=False,
        help="Write name of out_file"
    )

    args = parser.parse_args()
    count = args.count
    hosts = []

    if not is_positive_int_value(count):
        parser.error('Wrong number of requests. It must be positive and integer')

    if args.hosts:
        hosts = args.hosts.split(',')
    elif args.file:
        hosts = load_hosts_from_file(args.file)

    hosts=valid_urls(hosts)

    if not hosts:
        parser.error('Invalid type of host')

    results = []
    if parallel_version:
        print('parallel version')
        start = time.time()
        max_workers = min(10, len(hosts))
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(test_host, host, count) for host in hosts}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        end = time.time()
        print(f'total operating time of the program {end - start}')
    else:
        print('linear version')
        start = time.time()
        for host in hosts:
            statistics = test_host(host, count)
            results.append(statistics)
        end = time.time()
        report_text = format_statistics(results)
        print(report_text)
        print(f'total operating time of the program {end - start}')

    report_text = format_statistics(results)

    if args.out:
        load_statistics_to_file(args.out, report_text)
    else:
        print(report_text)


if __name__ == "__main__":
    main()
