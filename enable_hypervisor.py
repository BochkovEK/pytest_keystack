import openstack
import requests
import config

conn = openstack.connect(cloud=config.CLOUD_NAME)
auth = conn.auth
token = conn.auth_token

# domain = auth['auth_url'].split('//')[-1].split(':')[0]  # from https://10.10.10.10:5000 to 10.10.10.10 or demo.local
domain = auth['auth_url'].split(':')[0]  # from https://10.10.10.10:5000 to https://10.10.10.10 or https://demo.local

# print(auth)
# print(domain)

def hv_list():
    print('Check hypervisors...')
    hosts = []
    for hv in conn.compute.hypervisors(details=True, with_servers=True):
        print({'name': hv.name, 'ip': hv.host_ip, 'state': hv.state, 'status': hv.status})
        hosts.append(hv)
    return hosts


def rise_up_nova_request(hv):
    print(f"Try to rise up nova for {hv.name}...")
    response = requests.put(
        domain + config.URL_COMPUTE_SERVICE + '/enable',
        headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': token
        },
        verify='./haproxy_pem',
        json={
            "binary": "nova-compute",
            "host": hv.name,
        }
    )

    print(response.content)


def list_to_rise_nova():
    hv_to_rise_nova = []
    for hv in hv_list():
        if hv.state == 'down' or hv.status == 'disabled':
            print(f"Hypervisor: {hv.name} with nova state: {hv.state} and nova status: {hv.status} will add to tuple "
                  f"to rise nova")
            hv_to_rise_nova.append(hv)
    return hv_to_rise_nova


def rise_up_nova_tuple_of_hvs(list_of_hvs):
    print(f"Rise up nova for tuple hvs...")
    # print(type(list_of_hvs))
    # print(list_of_hvs)
    for hv in list_of_hvs:
        print(f"Rise nova on hv.name: {hv.name}")
        rise_up_nova_request(hv)


rise_up_nova_tuple_of_hvs(list_to_rise_nova())
