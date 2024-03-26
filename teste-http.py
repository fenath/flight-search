import requests


def main():
    url = 'https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/prices/cheap'
    params = {
        origin: 'CWB',
        page: 'None',
        currency: 'BRL',
        destination: 'FOR'
    }
    headers = {
        'X-Access-Token': '',
        'X-RapidAPI-Key': '',
        'X-RapidAPI-Host': 'travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com'
    }


if __name__=='__main__':
    main()
