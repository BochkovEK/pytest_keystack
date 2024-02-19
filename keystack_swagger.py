import requests
import openstack
import config

conn = openstack.connect(cloud=config.CLOUD_NAME)
auth = conn.auth

domain = auth['auth_url'].split('//')[1].split(':')[0]
# print(f"domain: {domain}")
region = config.CLOUD_NAME
# print(f"region name: {region}")


def get_token():
    print("Get token...")
    url = "https://" + domain + ":13000/login"
    token = requests.post(
        url,
        verify='./haproxy_pem',
        json={
            "login": auth['username'],
            "password": auth['password'],
            "user_domain_name": "Default"
        }
    )
    print(token.content)
    return token.json()['X-Auth-Token']


def get_compute_service_list(region=region, domain=domain):
    print("Get compute_service_list...")
    url = "https://" + domain + ":13000/" + region + "/nova_service_list"
    compute_service_list = requests.get(
        url,
        headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': get_token()
        },
        verify='./haproxy_pem',
    )
    print(compute_service_list.content)
    return compute_service_list


# get_token()
# get_compute_service_list()

