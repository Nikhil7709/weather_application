import requests

def scrape_data(region, parameter):
    url = f"https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/{parameter}/date/{region}.txt"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None


