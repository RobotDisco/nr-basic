import requests
import os
import time
import json

def handler(event,context):
    # For cookies and error handling
    session = requests.Session()
    session.hooks = {
    'response': lambda r, *args, **kwargs: r.raise_for_status()
    }


    #  Login
    # irritating hack because of SSL
    login_cookies = dict(login_service_login_newrelic_com_tokens="%7B%22token%22%3A+%22K22BZdbtrckArzJqjwEse8XEcjYkae2r8%2B5xouG2OXG2%2Bqr57e2aZawq0%2FoXL9Y0HWADxZK8PtInYMK3ew8gdoxXB5Bnen3ib%2Fv0BFUzObUSRoUpWdleV2atoDWMfctCz3cXf1402v68r%2BuZ0K0Z%2Fxah8MRo0eR6il%2Bm9A2ARC2PCQC%2F%2BZpGMOpXfxEl35MZNi%2BhwOHq9kwMJWLOOYu%2BuJtSlKbb%2BzihGExN9%2Fm2MG0hn%2FWBUW2uw3Ixj0SzJ5KZyuAYCkg%2FR8qos5m%2Bgw5q7dMfa5Cwywto1goDk3ZWm03Nle0CQK13Diaw9atjhAnlcwTxphEIOdHXZrgZNV08XQ%3D%3D%22%2C+%22refresh_token%22%3A+%22PPiKl9am3OoviqibjLIRhyqoh7Z%2B7TDBdroGdvPVRH%2FlFLrWCG1quJQbYhdSw0VS5LsnqrdmSKVmD3QDkeo%2FKfhZjVI7TUJ4nK8cO3gTgPOdhEdlmh5%2Bkp151jQk5ek5rbSwfqbGbMyWMj5HCQ7Xwc%2BzMUqJCXjl02spFMvwfYSxrbhXSS0WOOsVZA55C1BXWsfoTNdFDPCNWzLIu4q2jyrXlQnlZm3d6%2B2RQ6v1l8s3oy0TeVxEt30jgLvY2%2FpfZynjgqeCGPPEQNszrquZUEoRn6x0rcPTaF5C3Whgryh5C%2FheVSOqpjYL1GawQH0KV%2BZVIX2wYq%2B1Y5M9y0wxsA%3D%3D%22%7D")
    login_response = session.post("https://login.newrelic.com/login", cookies = login_cookies)
    
    custom_headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json"
    }

    # Get users
    users_response = session.get(f"https://user-management.service.newrelic.com/accounts/{os.getenv('ACCOUNT_ID')}/users",  headers=custom_headers, cookies=login_cookies)
    
    # Determine which users need to be switched back to basic
    switch_to_basic = []
    for user in users_response.json():
        roles = [role['id'] for role in user['roles'] ]
        if int(os.getenv("ROLE_ID")) in roles: # check if in the auto role
            if user['user_tier_id'] == 0: #check if full role
                if user['last_access_at'] + int(os.getenv("TIMEOUT")) < time.time(): # check if the last access + timeout is less than the current timestamp
                    switch_to_basic.append(user['user_id'])

    # Update accounts
    for user_id in switch_to_basic:
        print(f"Switching {str(user_id)} back to basic")
        update_response = session.put(f"https://rpm.newrelic.com/user_management/accounts/{os.getenv('ACCOUNT_ID')}/users/{user_id}",
          headers=custom_headers,
          cookies=login_cookies,
          json={
              "account_view":{
                  "user_tier_id":1
               }
            }
        )
if __name__ == "__main__":
    handler({},{})
