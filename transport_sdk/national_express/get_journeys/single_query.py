'''Gets all the the tickets for a specific time and journey'''

import json

import requests
from requests.exceptions import HTTPError

URL_OUT = 'https://book.nationalexpress.com/nxrest/journey/search/OUT'
URL_IN = 'https://book.nationalexpress.com/nxrest/journey/search/IN'

session = requests.Session()

# def get_booking_fee(searchSessionKey, headers):

#     url = 'https://book.nationalexpress.com/nxrest/bookingfee/RESERVATION/DOMESTIC/1/NX/DEFAULT/'
#     url += searchSessionKey
    
#     response = session.get(url, headers=headers)

#     booking_fee = json.loads(response.text)["fee"]

#     return booking_fee

def get_nx_tickets(journey_type, outbound_date, outbound_time, fromStationId, toStationId, return_date=None, return_time=None, coachCard=False, outboundArriveByOrDepartAfter="DEPART_AFTER", operatorType="DOMESTIC", campaignId="DEFAULT", partnerId="NX", session=session):

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Referer': 'https://book.nationalexpress.com/coach/',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

    payload = {
        "coachCard": coachCard,
        "campaignId": campaignId,
        "partnerId": partnerId,
        "outboundArriveByOrDepartAfter": outboundArriveByOrDepartAfter,
        "journeyType": journey_type,
        "operatorType": operatorType,
        "leaveDateTime": {
            "date": outbound_date,
            "time": outbound_time
            },
        "passengerNumbers": {
            "numberOfAdults": 1,
            "numberOfBabies": 0,
            "numberOfChildren": 0,
            "numberOfDisabled": 0,
            "numberOfSeniors": 0,
            "numberOfEuroAdults": 0,
            "numberOfEuroSeniors": 0,
            "numberOfEuroYoungPersons": 0,
            "numberOfEuroChildren": 0
            },
        "coachCardNumbers": {
            "numberOnDisabledCoachcard": 0,
            "numberOnSeniorCoachcard": 0,
            "numberOnYouthCoachcard": 0
            },
        "returnDateTime": {
            "date": return_date,
            "time": return_time
            },
        "fromToStation": {
            "fromStationId": fromStationId,
            "toStationId": toStationId
            },
        "onDemand": False,
        # "fromStationName": "LONDON (Most Popular)",
        # "toStationName": "BATH (Bus Station)",
        "languageCode":"en",
        "channelsKey":"DESKTOP",
    }

    try:
        response = session.post(URL_OUT, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')

    print(response)
    
    print(response.text)

    return response


def print_response(response):

    print()

    response_text = json.loads(response.text)

    for journey in response_text['journeyCommand']:

        departureStop = journey['legs'][0]['departureStop']
        departureStopId = journey['legs'][0]['departureStopId']

        destinationStop = journey['legs'][-1]['destinationStop']
        destinationStopId = journey['legs'][-1]['destinationStopId']

        departureDate = journey['departureDateTime'].split('T')[0]
        departureTime = journey['departureDateTime'].split('T')[1][:-3]

        arrivalDate = journey['arrivalDateTime'].split('T')[0]
        arrivalTime = journey['arrivalDateTime'].split('T')[1][:-3]

        fare = '£' + str(journey['fare']['amountInPennies'])[:-2] + '.' + str(journey['fare']['amountInPennies'])[-2:]

        journeyId = journey['journeyId']

        print(f'{departureStop} [{departureTime}] → {destinationStop} [{arrivalTime}]')
        print(fare)
        print()


if __name__ == '__main__':
    
    response = get_nx_tickets(
        journey_type="SINGLE",
        outbound_time="17:00",
        outbound_date="05/08/2022",
        fromStationId="57000",
        toStationId="87025"
    )

    print_response(response)
