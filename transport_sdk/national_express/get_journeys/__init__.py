from proxy_rotator import bd_proxy_rotator, build_rotator
from transport_sdk.national_express.get_journeys.helpers import generate_headers


def single_request(payload, headers=generate_headers(), opener=build_rotator(deactivate_proxies=False)):

    '''This function makes 1 request to the national express API for a specific date and time.'''

    response = bd_proxy_rotator(
        url='https://book.nationalexpress.com/nxrest/journey/search/OUT',
        headers=headers,
        payload=payload,
        opener=opener
    )

    return response


def multi_request(initial_payload, time_range, date_range=None, headers=generate_headers(), deactivate_proxies=False):

    '''This function adds a series of single_requests to a queue in order to get all available tickets for a given time range and date range.'''

    pass



# ----------------------------------------------

if __name__ == '__main__':

    from bs4 import BeautifulSoup
    from transport_sdk.national_express.get_journeys.helpers import generate_payload, print_response

    response = single_request(
        payload=generate_payload(
            journey_type="SINGLE",
            outbound_time="17:00",
            outbound_date="05/08/2022",
            from_station_id="57000",
            to_station_id="87025"
        ),
        opener=build_rotator(deactivate_proxies=True)
    )

    soup = BeautifulSoup(response, 'html.parser')

    print(f'\nResponse size: {len(soup.text)} bytes\n')
    print_response(soup.text)
