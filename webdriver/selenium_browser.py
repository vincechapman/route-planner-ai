import colorama
from colorama import Fore, Style
colorama.init()

def init_browser():

    import os

    from dotenv import load_dotenv
    load_dotenv()

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    service = Service()
    service.path = os.environ.get('CHROMIUM_DRIVER') or 'chromedriver'

    options = Options()
    options.headless = True

    try:
        browser = webdriver.Chrome(options=options, service=service)
    except:
        browser = None
        print(f"\n{Fore.LIGHTRED_EX}🔴 Failed to create initialise selenium webdriver.{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.LIGHTGREEN_EX}🟢 Selenium webdriver started:{Style.RESET_ALL}\n{'-' * 50}\n")

    return browser


def close_browser(browser):
    browser.quit()
    print(f"\n{'-' * 50}\n{Fore.LIGHTMAGENTA_EX}🟣 Selenium webdriver closed{Style.RESET_ALL}\n")


class Browser(object):

    def __enter__(self):
        self.browser = init_browser()
        return self.browser

    def __exit__(self, exc_type, exc_value, exc_traceback):
        close_browser(self.browser)


with Browser() as b:
    print('do stuff')
    print(b)