import time
# import testinfra
import openstack
from openstack import exceptions
import config

# import environment
# import re
# import math

conn = openstack.connect(cloud=config.CLOUD_NAME)

affin_group_name = "test_affinity_group"

affin_group_prop = {
    'name': affin_group_name,
    'policy': "anti-affinity"
}


def server_group_list():
    sg_list = []
    for sg in conn.compute.server_groups():
        # print(sg.to_dict())
        sg_list.append(sg)
    return sg_list


def create_server_group(**attrs):
    affin_group_exist = False
    for sg in server_group_list():
        if sg.name == attrs.get('name'):
            affin_group_exist = True
            return sg
    if not affin_group_exist:
        print(f"Creating server group: \"{attrs.get('name')}\"...")
        sg = conn.compute.create_server_group(**attrs)
        print(f"Finding server group: \"{attrs.get('name')}\"...")
        print(conn.compute.find_server_group(attrs.get('name'), ignore_missing=True, all_projects=False))
        return sg


def delete_server_group(server_group_name):
    for sg in server_group_list():
        if sg.name == server_group_name:
            print(f"Deleting server group: \"{server_group_name}\"...")
            conn.compute.delete_server_group(sg.id, ignore_missing=True)


create_server_group(**affin_group_prop)
# delete_server_group(affin_group_name)


# foo = {'name': 'Bogdan', 'posts_qty': 25}
# def get_posts_info(**kwargs):
#     print(kwargs)
# get_posts_info(**foo)


