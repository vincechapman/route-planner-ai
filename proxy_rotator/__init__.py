def build_rotator(deactivate_proxies=False, username=None, password=None, location='-country-gb', port=22225):

    # ----------------------------------------------------------------------
    # Importing env vars for bright data

    import os
    from dotenv import load_dotenv
    load_dotenv()

    username = username or os.environ['BRIGHTDATA_DATACENTER_USERNAME']
    password = password or os.environ['BRIGHTDATA_DATACENTER_PASSWORD']

    # ----------------------------------------------------------------------
    # Building an opener that uses the proxies provided by bright data.
    # These proxies will be selected randomly from the current IP selection pool. So the IP should change with each request. If our proxies start getting worn out we can probably build our program so that it automatically refreshes the selection pool using BrightData's API.

    from urllib.request import build_opener, ProxyHandler

    if not deactivate_proxies:
        opener = build_opener(
            ProxyHandler(
                {
                    'http': f'http://{username}{location}:{password}@zproxy.lum-superproxy.io:{port}',
                    'https': f'http://{username}{location}:{password}@zproxy.lum-superproxy.io:{port}'
                }
            )
        )
    else:
        opener = build_opener()

    return opener


def bd_proxy_rotator(url, payload=None, headers=None, method=None, opener=build_rotator()):

    from urllib.request import Request

    if payload is not None:
        import json
        payload = json.dumps(payload)
        payload = payload.encode()

    if headers:
        response = opener.open(Request(url=url, data=payload, headers=headers, method=method))
    else:
        response = opener.open(Request(url=url, data=payload, method=method))

    return response
