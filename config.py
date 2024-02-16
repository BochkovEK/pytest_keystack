DEFAULT_INSTALL_HOME = '/installer'
CLOUD_NAME = 'ebochkov-ks-sber'
SERVER_NAME = 'test_vm_sdk'
NETWORK_NAME = 'test_network_sdk'
NETWORK_STATE_NAME = 'pub_net'
IMAGE_NAME = 'test_image_sdk'
IMAGE_STATE_NAME_CIRROS = 'cirros-0.5.2-x86_64-disk'
IMAGE_STATE_NAME_UBUNTU = 'ubuntu-20.04-x64'
IMAGE_STATE_NAME_UBUNTU2 = 'ubuntu-20.04-server-cloudimg-amd64'
SOURCE_CIRROS_IMAGE = './cirros-0.5.2-x86_64-disk.img'
SOURCE_UBUNTU_IMAGE = './ubuntu-20.04-server-cloudimg-amd64.img'
FLAVOR_NAME = 'test_flavor_sdk'
INIT_FOLDER = "~/keystack_test/"  # sed start_test.sh
SUBNET_NAME = 'test_subnet_sdk'
VOLUME_NAME = 'test_volume_sdk'
SEC_GROUP_NAME = 'test_security_group_sdk'
KEYPAIR_NAME = 'test_key_sdk'
KEYPAIR_FILE = f"test_key.pem"  # for remote (testing by PyCharm)
KEYPAIR_PUBL_FILE = f"test_key.pub"
INVENTORY_FILE = f"inventory"  # for stand (testing by pytest container)
STRESS_FILE = f"stress"
SCREEN_UBUNTU_DEB_FILE = f"screen_4.8.0-1ubuntu0.1_amd64.deb"
SCREEN_CENTOS_DEB_FILE = f"screen-4.6.2-12.el8.x86_64.rpm"
DISABLE_NETWORK_SCRIPT = f"disable_network.sh"
INSTALL_SCREEN_COMMAND = 'sudo apt -y install ./screen_4.8.0-1ubuntu0.1_amd64.deb'
SCREEN_SESSION = 'screen'  # screen session name

NETWORK_PROP = {
    'name': NETWORK_NAME,
    'shared': True,
    'is_router_external': True,
    'provider_network_type': 'flat',
    'provider_physical_network': 'physnet1',
}

CIDR_BASE = '10.0.0.'

SUBNET_PROP = {
    'name': SUBNET_NAME,
    # 'cidr': '10.1.0.0/24',
    # 'gateway_ip': '10.1.0.1',
    # 'allocation_pools': [{'start': '10.1.0.11', 'end': '10.1.0.100'}],
    'cidr': f"{CIDR_BASE}0/24",
    'gateway_ip': f"{CIDR_BASE}1",
    'allocation_pools': [{'start': f"{CIDR_BASE}11", 'end': f"{CIDR_BASE}100"}],
    'ip_version': '4',
}

# LCM = "local://"  # for stand (testing by pytest container)
LCM = "paramiko://root@10.0.0.10"
CMPT1 = "paramiko://root@10.0.0.21"
CMPT2 = "paramiko://root@10.0.0.22"
CTRL1 = "paramiko://root@10.0.0.11"
CTRL2 = "paramiko://root@10.0.0.12"
CTRL3 = "paramiko://root@10.0.0.13"
LVM = "paramiko://root@10.0.0.9"
HOSTS = {
        'lcm': LCM,
        'cmpt-1': CMPT1,
        'cmpt-2': CMPT2,
        'ctrl-1': CTRL1,
        'ctrl-2': CTRL2,
        'ctrl-3': CTRL3,
        'lvm': LVM
}
SKIP_TEST = True
SKIP_CLEANUP = True
# =============================================================
# Gitlab
GITLAB_PASS_FILE_NAME = 'gitlab_root_password'
GITLAB_PREFIX = "https://"  # sed start_test.sh
GITLAB_MAIN_PROJECTS = ['keystack/agent-kolla',
                        'keystack/agent-gitlab'
                        ]
GITLAB_PROJECT_SET = {
        "agent-gitlab",
        "agent-kolla",
        "ci",
        "dib-config",
        "kolla-ansible",
        "kolla-configs",
        "rally-openstack",
        "tempest",
        "ansible-collection-kolla",
        "agent-dib",
        "log-ansible"
        }
# =============================================================
# Docker
LCM_DOCKERS = [
        'web',
        'gitlab-runner',
        'syslog',
        'gitlab',
        'portainer',
        'vault',
        'nexus'
]
LVM_DOCKERS = [
        'cinder_backup',
        'cinder_volume',
        'iscsid',
        'prometheus_cadvisor',
        'prometheus_node_exporter',
        'cron',
        'kolla_toolbox'
]
CMPT_DOCKERS = [
        'consul',
        'neutron_ovn_metadata_agent',
        'ovn_controller',
        'openvswitch_vswitchd',
        'openvswitch_db',
        'nova_compute',
        'nova_libvirt',
        'nova_ssh',
        'iscsid',
        'prometheus_libvirt_exporter',
        'prometheus_cadvisor',
        'prometheus_node_exporter',
        'cron',
        'kolla_toolbox'
]
CTRL_DOCKERS = [
        'consul',
        'octavia_worker',
        'octavia_housekeeping',
        'octavia_health_manager',
        'octavia_driver_agent',
        'octavia_api',
        'grafana',
        'barbican_worker',
        'barbican_keystone_listener',
        'barbican_api',
        'horizon',
        'heat_engine',
        'heat_api_cfn',
        'heat_api',
        'neutron_server',
        'ovn_controller',
        'ovn_northd',
        'ovn_sb_db',
        'ovn_nb_db',
        'openvswitch_vswitchd',
        'openvswitch_db',
        'nova_novncproxy',
        'nova_conductor',
        'nova_api',
        'nova_scheduler',
        'placement_api',
        'cinder_scheduler',
        'cinder_api',
        'kibana',
        'keystone',
        'keystone_fernet',
        'keystone_ssh',
        'rabbitmq',
        'prometheus_blackbox_exporter',
        'prometheus_openstack_exporter',
        'prometheus_alertmanager',
        'prometheus_cadvisor',
        'prometheus_memcached_exporter',
        'prometheus_haproxy_exporter',
        'prometheus_mysqld_exporter',
        'prometheus_node_exporter',
        'prometheus_server',
        'memcached',
        'mariadb_clustercheck',
        'mariadb',
        'redis_sentinel',
        'redis',
        'keepalived',
        'haproxy',
        'cron',
        'kolla_toolbox'
]
# =============================================================
# Nexus
NEXUS_PASS_FILE_NAME = 'nexus_admin_password'
# =============================================================
# HA Test 1
HA_DOCKER_CONTAINER_NAME = 'consul'
WAIT_HA_TEST1 = 120  # seconds
# ============================================================
# DRS Test 1
DRS_DOCKER_CONTAINER_NAME = 'drs'
VM_QTY_DRS_TEST1 = 2  # VM migration test from one loaded host to a free one
# STRESS_COMMAND1 = '\"yes > /dev/null &\"'
# STOP_COMMAND1 = 'killall yes'
WAIT_TEST1 = 5  # seconds
WAIT_CYCLES1 = 70  # retrying
# WAIT_REMIGRATE1 = 180  # seconds
# ============================================================
# DRS Test 2
VM_QTY_DRS_TEST2 = 3  # Test for the absence of VM migration from a loaded host to a loaded one
WAIT_TEST2 = 5  # seconds
WAIT_CYCLES2 = 35  # retrying
# WAIT_REMIGRATE2 = 100  # seconds
# ============================================================
# 'prometheus_memcached_exporter'
# compute_hosts = testinfra.get_hosts(f"ansible://deployment?ansible_inventory={config.INVENTORY_FILE}")
# lcm_host = testinfra.get_hosts(f"ansible://deployment?ansible_inventory={config.INVENTORY_FILE}")
