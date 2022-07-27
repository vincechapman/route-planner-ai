URL_OUT = 'https://book.nationalexpress.com/nxrest/journey/search/OUT'
URL_IN = 'https://book.nationalexpress.com/nxrest/journey/search/IN'


def generate_headers(random=False):

    # If program stops working, check if the headers below match what's being used on the national express website.

    if random:
        'Add randomisation here'
    else:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': 'https://book.nationalexpress.com/coach/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'Windows',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

    return headers


def generate_payload(journey_type, outbound_date, outbound_time, from_station_id, to_station_id, number_of_adults=1, number_of_babies=0, number_of_children=0, number_of_disabled=0, number_of_seniors=0, number_of_euro_adults=0, number_of_euro_seniors=0, number_of_euro_young_persons=0, number_of_euro_children=0, return_date=None, return_time=None, coach_card=False, outbound_arrive_by_or_depart_after="DEPART_AFTER", operator_type="DOMESTIC", campaign_id="DEFAULT", partner_id="NX", number_of_disabled_coachcard=0, number_of_senior_coachcard=0, number_of_youth_coachcard=0, on_demand=False, language_code='en', channels_key='DESKTOP'):

    # If the program stops working, check that the payload below is the same as what is being used on the national express website.

    payload = {
        "coachCard": coach_card,
        "campaignId": campaign_id,
        "partnerId": partner_id,
        "outboundArriveByOrDepartAfter": outbound_arrive_by_or_depart_after,
        "journeyType": journey_type,
        "operatorType": operator_type,
        "leaveDateTime": {
            "date": outbound_date,
            "time": outbound_time
            },
        "passengerNumbers": {
            "numberOfAdults": number_of_adults,
            "numberOfBabies": number_of_babies,
            "numberOfChildren": number_of_children,
            "numberOfDisabled": number_of_disabled,
            "numberOfSeniors": number_of_seniors,
            "numberOfEuroAdults": number_of_euro_adults,
            "numberOfEuroSeniors": number_of_euro_seniors,
            "numberOfEuroYoungPersons": number_of_euro_young_persons,
            "numberOfEuroChildren": number_of_euro_children
            },
        "coachCardNumbers": {
            "numberOnDisabledCoachcard": number_of_disabled_coachcard,
            "numberOnSeniorCoachcard": number_of_senior_coachcard,
            "numberOnYouthCoachcard": number_of_youth_coachcard
            },
        "returnDateTime": {
            "date": return_date,
            "time": return_time
            },
        "fromToStation": {
            "fromStationId": from_station_id,
            "toStationId": to_station_id
            },
        "onDemand": on_demand,
        # "fromStationName": "LONDON (Most Popular)",
        # "toStationName": "BATH (Bus Station)",
        "languageCode": language_code,
        "channelsKey": channels_key,
    }

    return payload


def print_response(response):

    import json

    print()

    response_text = json.loads(response)

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


# def get_booking_fee(searchSessionKey, headers):

#     url = 'https://book.nationalexpress.com/nxrest/bookingfee/RESERVATION/DOMESTIC/1/NX/DEFAULT/'
#     url += searchSessionKey
    
#     response = session.get(url, headers=headers)

#     booking_fee = json.loads(response.text)["fee"]

#     return booking_fee

from typing import Dict, Any

def dict_hash(dictionary: Dict[str, Any]) -> str:
    
    import hashlib
    import json
    
    dhash = hashlib.md5()
    
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    
    dhash.update(encoded)
    
    return dhash.hexdigest()