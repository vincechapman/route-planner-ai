# Third fallback tries to get the data using selenium and beautiful soup.

def fallback_3(payload, payload_hash, add_to_database=True):

    from bs4 import BeautifulSoup
    from selenium_browser import Browser

    try:

        with Browser() as browser:

            print('Ta da!')

            # URL = 'https://book.nationalexpress.com/nxrest/journey/search/OUT'

            # browser.get(URL)

            # # Need to a few more steps here to get to the right page (e.g. button clicks, filling out forms etc.)
            
            # soup = BeautifulSoup(browser.page_source, 'html.parser')

            # print(soup.text)

            from datetime import datetime
            request_time = datetime.utcnow()

            response = None

    except:

        print('Selenium not working.')

        response = None

    else:

        if add_to_database:
            from transport_sdk.national_express.get_journeys.helpers import add_to_postgres
            add_to_postgres(response, payload_hash, request_time)
        else:
            print('add_to_database set to False')

    finally:

        return response