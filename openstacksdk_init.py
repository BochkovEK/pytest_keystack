import openstack
import config
import pprint

# Initialize and turn on debug logging
# openstack.enable_logging(debug=True)

# Initialize connection
CLOUD_NAME = config.CLOUD_NAME
conn = openstack.connect(cloud=CLOUD_NAME)

# List the servers
for server in conn.list_servers():
    pprint.pprint(server.to_dict())
    # print(server)

    # 'power_state': 1,
    # 'private_v4': '',
    # 'private_v6': '',
    # 'progress': 0,
    # 'project_id': 'e124970547804711a9efeff2b09e21d7',
    # 'public_v4': '10.224.140.86',
    # 'public_v6': '',
    # 'ramdisk_id': '',
    # 'reservation_id': 'r-glalp3r7',
    # 'root_device_name': '/dev/vda',
    # 'scheduler_hints': None,
    # 'security_groups': [{'name': 'default'}],
    # 'server_groups': None,
    # 'status': 'ACTIVE',

