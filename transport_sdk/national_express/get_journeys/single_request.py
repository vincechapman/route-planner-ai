import json

from datetime import datetime

from transport_sdk.national_express.get_journeys.helpers import generate_headers, dict_hash
from proxy_rotator import build_rotator, bd_proxy_rotator


def single_request(payload, headers=generate_headers(), opener=build_rotator(deactivate_proxies=False), add_to_database=True):

    '''This function makes 1 request to the national express API for a specific date and time.'''

    payload_hash = dict_hash(payload)

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

        # Add all of these back to the queue and have them called in a random order. These fallbacks should apply specifically to INCAPSULA ERRORS

        # fallback_1 - Try datacentre proxy again

        from transport_sdk.national_express.get_journeys.fallback_1 import fallback_1

        job = q.enqueue(
            f=fallback_1,
            payload=payload,
            payload_hash=payload_hash,
            headers=headers,
            add_to_database=add_to_database,
            retry=Retry(max=3, interval=[5, 30, 60]),
            job_id=payload_hash + '_fb_1'
            )

        print(f'Fallback 1 - Initiated for {job}\n')

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



if __name__ == '__main__':

    from transport_sdk.national_express.get_journeys.helpers import generate_payload

    single_request(
        payload=generate_payload(
            journey_type='SINGLE',
            outbound_date='07/08/2022',
            outbound_time='17:00',
            from_station_id='57000',
            to_station_id='87025'),
        headers=generate_headers(),
        opener=build_rotator(deactivate_proxies=True),
        add_to_database=True
    )