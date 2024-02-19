import openstack
import requests
import config

conn = openstack.connect(cloud=config.CLOUD_NAME)
auth = conn.auth

print(auth)

token = requests.post(
        auth['auth_url'] + "/v3/auth/tokens",
        headers={
            'Content-Type': 'application/json'
        },
        verify='./haproxy_pem',
        json={
            "auth": {
                    "identity": {
                        "methods": ["password"],
                        "password": {
                            "user": {
                                "name": auth['username'],
                                "domain": {"id": "default"},
                                "password": auth['password']
                            }
                        }
                    }
                }
            }
        )

print(token.json())

