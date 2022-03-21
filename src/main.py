import json
from downloader import Downloader

if __name__ == '__main__':
    try:
        config = json.load(open('config.json'))
        cookie, url = config['sessionCookie'], config['resourceUrl']

        if not cookie or not url:
            print('Session cookie or resource URL missing from config.json')
            exit()
        
        downloader = Downloader(cookie, url)
        downloader.download()

    except FileNotFoundError:
        print("FATAL ERROR: Could not find config file")
    except json.decoder.JSONDecodeError:
        print("FATAL ERROR: Could not read config file, invalid JSON")
    except Exception as e:
        print("Unknown error: " + str(e))