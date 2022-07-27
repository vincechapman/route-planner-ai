import colorama
from colorama import Fore, Style
colorama.init()

from proxy_rotator import bd_proxy_rotator, build_rotator
from transport_sdk.national_express.get_journeys.helpers import generate_headers, dict_hash

from route_finder import create_app
app = create_app()

from route_finder.db import DatabaseConnection, get_postgres_db

def multi_request(initial_payload, time_range=None, date_range=None, headers=generate_headers(), opener=build_rotator(deactivate_proxies=False)):

    '''This function adds a series of single_requests to a queue in order to get all available tickets for a given time range and date range.'''

    payload = initial_payload

    from transport_sdk.national_express.get_journeys.single_request import single_request
    

    # ---------------------------------------------------------------------------------------
    # Initialising queue

    from redis import Redis
    from rq import Queue, Retry

    q = Queue(name='nx_requests', connection=Redis())

    # q.empty() # Eventually remove this


    # ---------------------------------------------------------------------------------------
    # Set default date and time ranges if none have been provided.

    from datetime import datetime, timedelta

    if time_range is None:
        default_time = payload['leaveDateTime']['time']
        start_time = datetime.strptime(payload['leaveDateTime']['time'], '%H:%M').replace(minute=0)
        end_time = datetime.strptime(payload['leaveDateTime']['time'], '%H:%M').replace(minute=0)
    else:
        start_time = datetime.strptime(time_range[0], '%H:%M').replace(minute=0)
        end_time = datetime.strptime(time_range[1], '%H:%M').replace(minute=0)
    
    if date_range is None:
        default_date = payload['leaveDateTime']['date']
        start_date = datetime.strptime(default_date, '%d/%m/%Y')
        end_date = datetime.strptime(default_date, '%d/%m/%Y')
    else:
        start_date = datetime.strptime(date_range[0], '%d/%m/%Y')
        end_date = datetime.strptime(date_range[1], '%d/%m/%Y')


    # ---------------------------------------------------------------------------------------
    # Loop through given date and time ranges.

    with app.app_context():

        with DatabaseConnection(get_postgres_db()) as db:

            cursor = db.cursor()

            while start_date != end_date + timedelta(days=1):

                selected_date = start_date.strftime('%d/%m/%Y')
                print(f"\n{selected_date}")


                start_time_x = start_time # have to use two different variables as the time range iterates more than once and we need to be able to reset it using the original variable at the end of each loop.

                while start_time_x != end_time + timedelta(hours=1):

                    selected_time = start_time_x.strftime("%H:%M")

                    payload['leaveDateTime']['date'] = selected_date
                    payload['leaveDateTime']['time'] = selected_time

                    payload_hash = dict_hash(payload)

                    if not q.fetch_job(payload_hash):

                        cursor.execute('SELECT * FROM public.nx_journeys WHERE payload_hash = %s', (payload_hash,))

                        if not cursor.fetchone():

                            job = q.enqueue(
                                f=single_request,
                                payload=payload,
                                headers=headers,
                                opener=opener,
                                retry=Retry(max=3, interval=[5, 30, 60]),
                                job_id=payload_hash
                            )

                            print(f'{Fore.LIGHTMAGENTA_EX}✔️ {selected_time} | {payload_hash} added to the queue.{Style.RESET_ALL}')

                        else:

                            # UPDATE this to check recency of the data we have already, as the ticket prices change.

                            print(f'{Fore.LIGHTRED_EX}❌ {selected_time} | {payload_hash} is already in the database.{Style.RESET_ALL}')

                    else:

                        print(f'{Fore.LIGHTRED_EX}❌ {selected_time} | {payload_hash} has already been added to the queue.{Style.RESET_ALL}')

                    start_time_x += timedelta(hours=1)

                start_date += timedelta(days=1)
            
            print()

            print(f'{len(q)} items were added to the queue.')



# ----------------------------------------------

if __name__ == '__main__':

    from bs4 import BeautifulSoup
    from transport_sdk.national_express.get_journeys.helpers import generate_payload, print_response

    # MULTI REQUEST

    multi_request(
        initial_payload=generate_payload(
            journey_type="SINGLE",
            outbound_time="17:00",
            outbound_date="01/08/2022",
            from_station_id="57000",
            to_station_id="87025"),
        date_range=('5/8/2022', '6/8/2022'),
        time_range=('17:00', '19:00'),
        opener=build_rotator(deactivate_proxies=True)
    )



#     # SINGLE REQUEST

#     from bs4 import BeautifulSoup
#     from transport_sdk.national_express.get_journeys.helpers import generate_payload, print_response

#     response = single_request(
#         payload=generate_payload(
#             journey_type="SINGLE",
#             outbound_time="17:00",
#             outbound_date="05/08/2022",
#             from_station_id="57000",
#             to_station_id="87025"),
#         opener=build_rotator(deactivate_proxies=True)
#     )

#     soup = BeautifulSoup(response, 'html.parser')

#     print(f'\nResponse size: {len(soup.text)} bytes\n')
#     print_response(soup.text)
