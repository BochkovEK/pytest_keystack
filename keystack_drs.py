# table of request https://<VIP>:13000/

import openstack
import requests
import config
import keystack_swagger

conn = openstack.connect(cloud=config.CLOUD_NAME)
auth = conn.auth

domain = auth['auth_url'].split('//')[-1].split(':')[0]  # from https://10.10.10.10:5000 to 10.10.10.10 or demo.local
print(f"domain: {domain}")
region = config.CLOUD_NAME
print(f"region name: {region}")


def drs_configs_list(region=region, domain=domain):
    print("Get DRS config list...")
    url = "https://" + domain + ":13000/" + region + "/drs/configs"
    configs_list = requests.get(
        url,
        headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': keystack_swagger.get_token()
        },
        verify='./haproxy_pem',
    )
    print(f"DRS configs list: {configs_list.json()['configs']}")
    return configs_list.json()['configs']


def create_drs_config(region=region,
                      domain=domain,
                      metric_resolution=2,
                      metric_weight_cpu=1,
                      metric_weight_mem=0,
                      move_syn_diff_after=5,
                      move_syn_threshold=85,
                      name='test_conf',
                      exclude_enable='True',
                      exclude_list='server,project,pci'
                      ):
    print("Create DRS config...")
    url = "https://" + domain + ":13000/" + region + "/drs/configs"
    drs_config = requests.post(
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
    print(f"DRS config: {drs_config.json()}")
    return drs_config.json()


def delete_drs_config(config_id):
    print(f"Delete DRS config {config_id}...")
    config_id = str(get_drs_config(config_id))
    url = "https://" + domain + ":13000/" + region + "/drs/configs/" + config_id
    requests.delete(
        url,
        headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': keystack_swagger.get_token()
        },
        verify='./haproxy_pem',
    )
    drs_configs_list()


def delete_all_drs_config(configs_list=None):
    if not configs_list:
        configs_list = drs_configs_list()
    for cfg in configs_list:
        delete_drs_config(cfg['id'])


def get_drs_config(conf_id=None):
    print(f"Get drs config: {conf_id}")
    configs_list = drs_configs_list()
    for cfg in configs_list:
        # print(cfg['name'], cfg['id'])
        if cfg['name'] == conf_id or cfg['id'] == conf_id:
            print(f"DRS config: name: {cfg['name']} id: {conf_id or cfg['id']}")
            return cfg['id']
    print(f"DRS config: {conf_id} doesn't exist")
    return None


# create_drs_config(
#                       move_syn_threshold=65,
#                       name='foo_test',
# )
# drs_configs_list()
# get_drs_config('foo_test')
# delete_drs_config('foo_test')

