# table of request https://<VIP>:13000/

import openstack
import requests
import config
import keystack_swagger

conn = openstack.connect(cloud=config.CLOUD_NAME)
auth = conn.auth
# token = keystack_swagger.get_token()

domain = auth['auth_url'].split('//')[-1].split(':')[0]  # from https://10.10.10.10:5000 to 10.10.10.10 or demo.local
print(domain)
region = config.CLOUD_NAME
print(f"region name: {region}")

drs_prop = {
    'metric_resolution': 2,
    'metric_weight_cpu': 8,
    'metric_weight_mem': 0,
    'move_syn_diff_after': 1,
    'move_syn_threshold': 5,
    'name': 'test_conf',
    'exclude_enable': True,
    'exclude_list': 'server,project,pci'
}

def drs_configs_list(region=region, domain=domain):
    print("Get DRS config list...")
    url = "https://" + domain + ":13000/" + region + "/drs/configs"
    drs_configs_list = requests.get(
        url,
        headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': keystack_swagger.get_token()
        },
        verify='./haproxy_pem',
    )
    print(drs_configs_list.json())
    return drs_configs_list.json()


def create_drs_config(region=region,
                      domain=domain,
                      metric_resolution=2,
                      metric_weight_cpu=8,
                      metric_weight_mem=0,
                      move_syn_diff_after=1,
                      move_syn_threshold=5,
                      name='test_conf',
                      exclude_enable=True,
                      exclude_list='server,project,pci',
                      **kwargs):
    print("Create DRS config...")
    url = "https://" + domain + ":13000/" + region + "/drs/configs"
    drs_config = requests.get(
        url,
        headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': keystack_swagger.get_token()
        },
        verify='./haproxy_pem',
        json={
            "base_config": {
                "METRIC_RESOLUTION": metric_resolution,
                "METRIC_WEIGHT_CPU": metric_weight_cpu,
                "METRIC_WEIGHT_MEM": metric_weight_mem,
                "MOVE_SYN_DIFF_AFTER": move_syn_diff_after,
                "MOVE_SYN_THRESHOLD": move_syn_threshold
            },
            "name": name,
            "exclude_enable": exclude_enable,
            "exclude_list": exclude_list
        }
    )
    print(drs_config.json())
    return drs_config.json()


create_drs_config(drs_prop)
drs_configs_list()

