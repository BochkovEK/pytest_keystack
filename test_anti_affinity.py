import openstack.compute.v2.hypervisor

import config
import create_server_group
import openstack_resources
import pytest


# Test anit-affinity group
## Create
### Create anit-affinity groups

@pytest.mark.dependency()
def test_hypervisors():
    hv = openstack_resources.hypervisors_list()
    assert len(hv) >= 4

@pytest.mark.dependency(depends=['test_hypervisors'])
def test_anti_affin_creation():
    config.ANTI_AFFIN_GROUP_PROP['name'] = config.ANTI_AFFIN_GROUP_NAME + '_1'
    assert create_server_group.create_server_group(**config.ANTI_AFFIN_GROUP_PROP)
    config.ANTI_AFFIN_GROUP_PROP['name'] = config.ANTI_AFFIN_GROUP_NAME + '_2'
    assert create_server_group.create_server_group(**config.ANTI_AFFIN_GROUP_PROP)
    # assert create_server_group.find_server_group(config.ANTI_AFFIN_GROUP_NAME + '_1')
    # assert create_server_group.find_server_group(config.ANTI_AFFIN_GROUP_NAME + '_2')


## Test
## CleanUp
@pytest.mark.dependency(depends=['test_anti_affin_creation'])
def test_anti_affin_deletion():
    assert create_server_group.delete_server_group(config.ANTI_AFFIN_GROUP_NAME + '_1')
    assert create_server_group.delete_server_group(config.ANTI_AFFIN_GROUP_NAME + '_2')
