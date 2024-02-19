# Checking DRS container status UP\healthy (gitlab global prechecking)

import config
import openstack_server_groups
import openstack_hypervisors
import openstack_resources
import pytest


# Test anit-affinity group
## Precheck

@pytest.mark.skip(reason="debug")
@pytest.mark.dependency()
def test_alive_hypervisors():
    openstack_hypervisors.rise_up_nova_list_of_hvs(openstack_hypervisors.list_to_rise_nova())
    hvs_alive_list = openstack_hypervisors.hvs_alive_list()
    print(f"Cluster has {len(hvs_alive_list)} alive hypervisors")
    assert len(hvs_alive_list) >= 4

# Check drs configs and job exist

## Create
### Create anit-affinity groups


# @pytest.mark.skip(reason="debug")
@pytest.mark.dependency(depends=['test_alive_hypervisors'])
def test_anti_affin_creation():
    config.ANTI_AFFIN_GROUP_PROP['name'] = config.ANTI_AFFIN_GROUP_NAME + '_1'
    assert openstack_server_groups.create_server_group(**config.ANTI_AFFIN_GROUP_PROP)
    config.ANTI_AFFIN_GROUP_PROP['name'] = config.ANTI_AFFIN_GROUP_NAME + '_2'
    assert openstack_server_groups.create_server_group(**config.ANTI_AFFIN_GROUP_PROP)


## Test
## CleanUp
# @pytest.mark.dependency(depends=['test_anti_affin_creation'])
# def test_anti_affin_deletion():
#     assert create_server_group.delete_server_group(config.ANTI_AFFIN_GROUP_NAME + '_1')
#     assert create_server_group.delete_server_group(config.ANTI_AFFIN_GROUP_NAME + '_2')
