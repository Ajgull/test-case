import argparse
import sys
import asyncio
from linear_main import linear_test
from parallel_main import parallel_test
from async_main import async_test
import utils


def main():
    parser = argparse.ArgumentParser(description="HTTP-server tester\n"
                                                 "–H/--hosts hosts separated by commas without spaces\n"
                                                 "–C/--count number of requests\n"
                                                 "–F/--file name of file to read hosts, each from a new line\n"
                                                 "–O/--output name of file for uploading results\n"
                                                 "-T/--type of program (l - linear, p - parallel, a - async")

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

    parser.add_argument(
        "-T", "--type", type=str, required=True,
        help="Write type of program to run (l - linear, p - parallel, a - async)"
    )

    args = parser.parse_args()
    count = args.count
    hosts = []

    if args.hosts and args.file:
        print('Impossible to run program with -F and -H keys')
        sys.exit(1)

    if not utils.is_positive_int_value(count):
        parser.error('Wrong number of requests. It must be positive and integer')

    if args.hosts:
        hosts = args.hosts.split(',')
    elif args.file:
        hosts = utils.load_hosts_from_file(args.file)

    hosts = utils.valid_urls(hosts)

    if not hosts:
        parser.error('Invalid type of host')

    if args.type == 'l':
        report_text, total_time = linear_test(hosts, count)
    elif args.type == 'p':
        report_text, total_time = parallel_test(hosts, count)
    elif args.type == 'a':
        report_text, total_time = asyncio.run(async_test(hosts, count))
    else:
        raise ValueError('Invalid type of running program')

    if args.out:
        utils.load_statistics_to_file(args.out, report_text)
    else:
        print(report_text)

    print(f'total operating time of the program {total_time}')


if __name__ == "__main__":
    main()
