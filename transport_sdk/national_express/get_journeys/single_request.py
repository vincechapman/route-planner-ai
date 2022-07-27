from transport_sdk.national_express.get_journeys.helpers import generate_headers
from proxy_rotator import build_rotator, bd_proxy_rotator

def single_request(payload, headers=generate_headers(), opener=build_rotator(deactivate_proxies=False)):

    '''This function makes 1 request to the national express API for a specific date and time.'''

    response = bd_proxy_rotator(
        url='https://book.nationalexpress.com/nxrest/journey/search/OUT',
        headers=headers,
        payload=payload,
        opener=opener
    )

    return response