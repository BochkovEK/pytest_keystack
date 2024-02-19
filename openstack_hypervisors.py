import openstack
import requests
import config

conn = openstack.connect(cloud=config.CLOUD_NAME)
auth = conn.auth
token = conn.auth_token

# domain = auth['auth_url'].split(':')[0]  # from https://10.10.10.10:5000 to https://10.10.10.10 or https://demo.local
domain = auth['auth_url'].split('//')[-1].split(':')[0]  # from https://10.10.10.10:5000 to 10.10.10.10 or demo.local
# print(domain)
url = "https://" + domain + config.URL_COMPUTE_SERVICE + "/enable"
# print(url)

# print(auth)
# print(domain)


def hvs_list():
    print('Check hypervisors...')
    hvs = []
    for hv in conn.compute.hypervisors(details=True, with_servers=True):
        print({'name': hv.name, 'ip': hv.host_ip, 'state': hv.state, 'status': hv.status})
        hvs.append(hv)
    return hvs


def hvs_alive_list():
    print('Check alive hypervisors (nova-compute state: up, status: enabled)...')
    alive_hvs = []
    for hv in conn.compute.hypervisors(details=True, with_servers=True):
        print({'name': hv.name, 'ip': hv.host_ip, 'state': hv.state, 'status': hv.status})
        if hv.state == 'up' and hv.status == 'enabled':
            print(f"Hypervisor: {hv.name} with nova state: {hv.state} and nova status: {hv.status} "
                  f"will add to alive hvs list")
            alive_hvs.append(hv)
    return alive_hvs


def rise_up_nova_request(hv):
    print(f"Try to rise up nova for {hv.name}...")
    response = requests.put(
        url,
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
    for hv in hvs_list():
        if hv.state == 'down' or hv.status == 'disabled':
            print(f"Hypervisor: {hv.name} with nova state: {hv.state} and nova status: {hv.status} will add to list "
                  f"to rise nova")
            hv_to_rise_nova.append(hv)
    return hv_to_rise_nova


def rise_up_nova_list_of_hvs(list_of_hvs):
    if list_of_hvs:
        print(f"Rise up nova for hvs list ...")
        # print(type(list_of_hvs))
        # print(list_of_hvs)
        for hv in list_of_hvs:
            print(f"Rise nova on hv.name: {hv.name}")
            rise_up_nova_request(hv)

# rise_up_nova_tuple_of_hvs(list_to_rise_nova())
