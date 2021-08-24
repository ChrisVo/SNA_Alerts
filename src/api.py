import requests
import json

def get_token(username, password):
    url = f"https://{os.getenv('strapi_hostname')}/admin/login"

    payload = {"email": username, "password": password}
    headers = {
    'Content-Type': 'application/json;charset=utf-8'
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    if response.status_code == 200:
        token = response.json()['data']['token']
        return {"status_code": 200, "token": token}
    else:
        print("Couldn't get the token")
        return {"status_code": 500, "token": ""}

def get_flights(token):

    url = f"https://{os.getenv('strapi_hostname')}/delayed-flights"

    payload={}
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()

def check_flights(search_indicator, flights):
    flight_nums = []
    for flight in flights:
        flight_nums.append(flight['flight_num'])
    if search_indicator in flight_nums:
        return True
    else:
        return False

def add_flight_to_db(token, flight_num):
    url = f"https://{os.getenv('strapi_hostname')}/delayed-flights"

    payload = json.dumps({
    "flight_num": f"{flight_num}"
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


if __name__ == "__main__":
    token_payload = get_token(os.getenv('strapi_username'), os.getenv('strapi_password'))
    token = token_payload['token']

    # Error handling
    if token_payload['status_code'] != 200:
        print("[*] Couldn't get token")
        exit

    # get flights
    flights = get_flights(token)
    if not check_flights("WN3263", flights):
        add_flight_to_db(token, "WN5004")