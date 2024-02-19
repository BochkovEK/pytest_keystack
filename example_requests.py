import openstack
import requests
import config

conn = openstack.connect(cloud=config.CLOUD_NAME)
token = conn.auth_token

# print(token)

# Project list
response = requests.get(
    'https://10.224.140.99:5000/v3/projects',
    headers={
        'Content-Type': 'application/json',
        'X-Auth-Token': token
        },
    verify='./haproxy_pem'
)

print(response.content)
