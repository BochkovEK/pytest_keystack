import openstack
import config


conn = openstack.connect(cloud=config.CLOUD_NAME)
token = conn.auth_token
# print(token)

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


def find_server_group(server_group_name):
    print(f"Finding server group: \"{server_group_name}\"...")
    sg = conn.compute.find_server_group(server_group_name, ignore_missing=True, all_projects=False)
    if sg:
        print(f"Server group: \"{server_group_name}\" exists")
        return sg
    else:
        print(f"Server group: \"{server_group_name}\" not found")
        return None


def create_server_group(**attrs):
    sg = find_server_group(attrs.get('name'))
    if sg:
        return sg
    else:
        print(f"Creating server group: \"{attrs.get('name')}\"...")
        return conn.compute.create_server_group(**attrs)


def delete_server_group(server_group_name):
    sg = find_server_group(server_group_name)
    if sg:
        print(f"Deleting server group: \"{server_group_name}\"...")
        conn.compute.delete_server_group(sg.id, ignore_missing=True)
        if find_server_group(server_group_name):
            print(f"Server group: \"{server_group_name}\" was not deleted")
            return False
    return True


# create_server_group(**affin_group_prop)
# delete_server_group(affin_group_name)



