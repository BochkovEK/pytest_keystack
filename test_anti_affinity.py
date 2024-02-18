import config
import create_server_group
import openstack_resources
import pytest


# Test anit-affinity group
## Create
### Create anit-affinity groups
@pytest.mark.dependency()
def test_anti_affin_creation():
    config.ANTI_AFFIN_GROUP_PROP['name'] = config.ANTI_AFFIN_GROUP_NAME + '_1'
    create_server_group.create_server_group(**config.ANTI_AFFIN_GROUP_PROP)
    config.ANTI_AFFIN_GROUP_PROP['name'] = config.ANTI_AFFIN_GROUP_NAME + '_2'
    create_server_group.create_server_group(**config.ANTI_AFFIN_GROUP_PROP)


## Test
## CleanUp
