import openstack
import config

# Initialize and turn on debug logging
# openstack.enable_logging(debug=True)

# Initialize connection
CLOUD_NAME = config.CLOUD_NAME
conn = openstack.connect(cloud=CLOUD_NAME)

# List the servers
for server in conn.list_servers():
    print(server.to_dict())
    print(server)

