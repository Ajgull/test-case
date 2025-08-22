import time
import aiohttp
import asyncio
import utils


async def fetch(host: str, count: int) -> dict:
    success_count = 0
    fail_count = 0
    error_count = 0
    time_of_requests = []

    async with aiohttp.ClientSession() as session:
        for _ in range(count):
            try:
                start_time = time.time()
                async with session.get(host) as response:
                    await response.text()
                end_time = time.time()
                if 200 <= response.status < 400:
                    success_count += 1
                else:
                    fail_count += 1

                time_of_requests.append(round((end_time - start_time) * 1000, 3))
            except aiohttp.ClientError as e:
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


async def async_test(hosts: list, count: int) -> tuple:
    print('async version')

    tasks = [fetch(host, count) for host in hosts]
    start = time.time()
    results = await asyncio.gather(*tasks)
    end = time.time()

    report_text = utils.format_statistics(results)
    total_time = end - start

    return report_text, total_time
