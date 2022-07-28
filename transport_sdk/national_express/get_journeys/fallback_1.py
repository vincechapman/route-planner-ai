# First fallback just calls the main function again

import json

from datetime import datetime
from transport_sdk.national_express.get_journeys.helpers import generate_headers, dict_hash
from proxy_rotator import build_rotator, bd_proxy_rotator

def fallback_1(payload, payload_hash, headers=generate_headers(), add_to_database=True):

    import os
    from dotenv import load_dotenv
    load_dotenv()

    opener = build_rotator(
        username=os.environ['BRIGHTDATA_DATACENTER_USERNAME'],
        password=os.environ['BRIGHTDATA_DATACENTER_PASSWORD'],)

    print('\nTrying again with data center proxies!')

    try:

        response = bd_proxy_rotator(
            url='https://book.nationalexpress.com/nxrest/journey/search/OUT',
            headers=headers,
            payload=payload,
            opener=opener
        )

        request_time = datetime.utcnow()

        status_code = response.code
        response = json.load(response)

        # This checks if the request has been blocked by incapsula or some other blocking mechanism
        if status_code == 200 and not response['journeyCommand']:

            raise Exception("Request failed. Most likely blocked by incapsula. Or response JSON structure/naming has been updated.")

    except Exception as e:

        import colorama
        from colorama import Fore, Style
        colorama.init()

        print(Fore.LIGHTCYAN_EX)
        print('\nINCAPSULA ERROR!!!\n')
        print(Style.RESET_ALL)

        print(e)

        from redis import Redis
        from rq import Queue, Retry
        from rq.job import Job

        q = Queue('high', connection=Redis())

        print('This is where fallback 2 would be called.')

        from transport_sdk.national_express.get_journeys.fallback_2 import fallback_2

        job = q.enqueue(
            f=fallback_2,
            payload=payload,
            payload_hash=payload_hash,
            headers=headers,
            add_to_database=add_to_database,
            # retry=Retry(max=3, interval=[5, 30, 60]),
            job_id=payload_hash + '_fb_2'
            )

        print(f'\nFallback 2 - Initiated for {job}\n')

        job = Job.fetch(payload_hash, connection=Redis())

        response = job.result

    else:

        if add_to_database:
            from transport_sdk.national_express.get_journeys.helpers import add_to_postgres
            add_to_postgres(response, payload_hash, request_time)
        else:
            print('add_to_database set to False')

    finally:

        return response

