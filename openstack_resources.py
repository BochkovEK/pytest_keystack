import os
import time
import testinfra
import openstack
from openstack import exceptions
import config
import environment
import re
import math


conn = openstack.connect(cloud=config.CLOUD_NAME)
# vm_os_name = config.SOURCE_IMAGE.split('/')[1].split('-')[0]  # cirros or ubuntu
keypair_file_name = config.KEYPAIR_FILE  # .split('/')[-1]  # test_key.pem
lcm_host_infra = testinfra.get_host(config.LCM)
vms_with_processes = []


# for server in conn.compute.servers():
#     print(dir(server))


# def get_host_infra_by_inventory()
#     pass

# Check if all elements in a list are identical
def all_equal(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)


def get_config_folder():
    config_folder = environment.INSTALL_HOME
    if not config_folder:
        return f"{config.DEFAULT_INSTALL_HOME}/config/"
    else:
        return f"{environment.INSTALL_HOME}/config/"


def get_hosts_cpus():
    config_folder = get_config_folder()
    cpu_list = []
    for hv in conn.compute.hypervisors(details=True, with_servers=True):
        # cmd_hypervisors_info = lcm_host_infra.run(f". {config_folder}openrc;"
        #                                           f" openstack host show {hv.name} | grep total")
        cmd_hypervisors_info = lcm_host_infra.check_output(f". {config_folder}openrc;"
                                                  f" openstack hypervisor list --long | grep {hv.name}")
        # print(cmd_hypervisors_info.stdout, cmd_hypervisors_info.stderr)
        cpu = cmd_hypervisors_info.split("|")[7].strip(" ")
        # print(cmd_hypervisors_info.stdout, cmd_hypervisors_info.stderr)
        # cpu = cmd_hypervisors_info.stdout.split("(total)")[1].split("|")[1].strip(" ")
        cpu_list.append(cpu)
        print(f"{hv.name} cpu: {cpu}")

    if all_equal(cpu_list):
        return int(cpu_list[0])
    else:
        return False


def get_hosts_ram():
    config_folder = get_config_folder()
    ram_list = []
    for hv in conn.compute.hypervisors(details=True, with_servers=True):
        cmd_hypervisors_info = lcm_host_infra.check_output(f". {config_folder}openrc;"
                                                  f" openstack hypervisor list --long | grep {hv.name}")
        # print(cmd_hypervisors_info.stdout, cmd_hypervisors_info.stderr)
        ram = cmd_hypervisors_info.split("|")[9].strip(" ")
        ram_list.append(ram)
        print(f"{hv.name} ram: {ram}")

    if all_equal(ram_list):
        ram_on_hosts = int(ram_list[0])
        start_ram_value = 256
        for n in range(10):
            # print(ram_on_hosts - start_ram_value*2**n)
            if ram_on_hosts - start_ram_value*2**n < 0:
                return start_ram_value*2**n
    else:
        return False


def get_stress_cmd(cpu=0, ram=0, timeout=1):
    # print(f"starting stress on cpu: {cpu}, ram: {ram}...")
    cpu_string = f"-c {cpu}"
    ram_string = f"--vm 1 --vm-bytes {ram}M --vm-keep"
    if cpu == 0:
        cpu_string = ""
    if ram == 0:
        ram_string = ""
    if not (cpu or ram):
        return None
    return f"screen -d -m -S {config.SCREEN_SESSION} ./stress {cpu_string} {ram_string} --timeout {timeout}s"


def hypervisors_list():
    hosts = []
    for hv in conn.compute.hypervisors(details=True, with_servers=True):
        print(hv.name)
        # hv_obj = conn.compute.find_hypervisor(hv.name)
        if hv and hv.state == 'up' and hv.status == 'enabled':
            print({'name': hv.name, 'ip': hv.host_ip, 'state': hv.state, 'status': hv.status})
            # hosts.append(hv_dict)
            hosts.append(hv)
        elif hv and hv.state == 'up' and hv.status != 'enabled':
            print(f"nova-compute doesnt enabled on {hv.name}\n"
                  f"try to enabling...")
            config_folder = get_config_folder()
            # host = get_host_infra_by_ip(hv.host_ip)
            print(f"lcm executing command: . {config_folder}openrc; openstack compute service"
                  f" set --enable {hv.name} nova-compute")
            cmd_enable_nova = lcm_host_infra.run(f". {config_folder}openrc; openstack compute service"
                                                 f" set --enable {hv.name} nova-compute")
            print(cmd_enable_nova.stdout, cmd_enable_nova.stderr)
            cmd_hypervisors_list = lcm_host_infra.run(f". {config_folder}openrc; openstack hypervisor show {hv.name}"
                                                      f" | grep status")
            print(cmd_hypervisors_list.stdout, cmd_hypervisors_list.stderr)
            hv = conn.compute.find_hypervisor(hv.name, details=True)  # , with_servers=True)
            if hv and hv.state == 'up' and hv.status == 'enabled':
                print({'name': hv.name, 'ip': hv.host_ip, 'state': hv.state, 'status': hv.status})
                # hosts.append(hv_dict)
                hosts.append(hv)

    print(f"hv list:\n{hosts}")

    return hosts


def get_vms_list_from_hv(hv_name):
    vm_list = []
    for server in conn.compute.servers():
        if server.hypervisor_hostname == hv_name:
            vm_list.append(server)
    return vm_list


def network_list():
    for network in conn.network.networks():
        print(network)


def ports_list():
    for port in conn.network.ports():
        print(port)


def security_groups_list():
    for port in conn.network.security_groups():
        print(port)


def create_security_group(recreate=False):
    if recreate:
        for port in conn.network.security_groups():
            if port.name == config.SEC_GROUP_NAME:
                conn.network.delete_security_group(port)
                print(f"\t\tsecurity group {config.SEC_GROUP_NAME} deleted")

    if conn.network.find_security_group(config.SEC_GROUP_NAME):
        print(f"\tsecurity group {config.SEC_GROUP_NAME} already exists")
        return {'name': config.SEC_GROUP_NAME}
    else:
        print(f"\tcreating security group {config.SEC_GROUP_NAME}")
        sec_group = conn.network.create_security_group(
            name=config.SEC_GROUP_NAME)

        print(f"\t\tsecurity group {sec_group.name} created")

        conn.network.create_security_group_rule(
            security_group_id=sec_group.id,
            direction='ingress',
            remote_ip_prefix='0.0.0.0/0',
            protocol='TCP',
            port_range_max='22',
            port_range_min='22',
            ethertype='IPv4')

        print(f"\t\tcp 22 rule was add to {sec_group.name}")
        return {'name': sec_group.name}


def create_network(name=config.NETWORK_NAME, recreate=False):
    network_state = conn.network.find_network(config.NETWORK_STATE_NAME)
    if network_state:
        print(f"\tstate network: {config.NETWORK_STATE_NAME} already exists")
        return network_state
    if recreate:
        for network in conn.network.networks():
            if network.name == config.NETWORK_NAME:
                conn.network.delete_network(network)
                print(f"\t\tnetwork {config.NETWORK_NAME} deleted")

    network = conn.network.find_network(name)

    if network:
        print(f"\tnetwork {name} already exists")
    else:
        try:
            print(f"\tcreating network {name}")
            network = conn.network.create_network(**config.NETWORK_PROP)
            subnet_prop = config.SUBNET_PROP.copy()
            subnet_prop['network_id'] = network.id
            conn.network.create_subnet(**subnet_prop)
            print(f"\t\tnetwork {name} created")
            # return network.id
        except exceptions.HttpException as e:
            print(f"message: {e.message}, code: {e.status_code}")
            # print(dir(e))
            # print(e.errno)

    return network


def create_keypair(recreate=False):
    if recreate:
        for keypair in conn.compute.keypairs():
            if keypair.name == config.KEYPAIR_NAME:
                conn.compute.delete_keypair(keypair)
                print(f"\t\tkeypair {config.KEYPAIR_NAME} deleted")

    keypair = conn.compute.find_keypair(config.KEYPAIR_NAME)

    if keypair:
        print(f"\tkeypair {config.KEYPAIR_NAME} already exists")
    else:
        print(f"\tcreating keypair {config.KEYPAIR_NAME}")
        public_key = open(config.KEYPAIR_PUBL_FILE, 'r').read()
        keypair = conn.compute.create_keypair(name=config.KEYPAIR_NAME, public_key=public_key)
        print(f"\tkeypair:\n\t{keypair.public_key}")
        print(f"\t\tkeypair {config.KEYPAIR_NAME} created")

    return keypair


def check_spec_in_flavor_name(flavor_name, spec_name):
    if spec_name in flavor_name:
        spec_in_flavor_name = re.search(r"\d+$", flavor_name.split(spec_name)[0])
        if spec_in_flavor_name:
            spec = spec_in_flavor_name.group(0)
            print(f"\t\tflavor: {flavor_name}, spec: {spec} {spec_name}")
            return spec
    print(f"\t\tflavor name {flavor_name} has no spec: {spec_name} data")
    return None


def create_flavor(name=config.FLAVOR_NAME+'-1cpu-256mb', vcpus=1, ram=256, disk=0, recreate=False):
    if recreate:
        for flavor in conn.compute.flavors():
            if flavor.name == name:
                conn.compute.delete_flavor(flavor)

    flavor = conn.compute.find_flavor(name)

    if flavor:
        print(f"\tflavor {name} already exists")
    else:
        print(f"\tcreating flavor {name}")
        vcpu_spec_from_flavor_name = check_spec_in_flavor_name(name, 'cpu')
        if vcpu_spec_from_flavor_name:
            vcpus = vcpu_spec_from_flavor_name
        ram_spec_from_flavor_name = check_spec_in_flavor_name(name, 'mb')
        if ram_spec_from_flavor_name:
            ram = ram_spec_from_flavor_name
        flavor_prop = {
            'name': name,
            'disk': disk,
            'ram': ram,
            'vcpus': vcpus,
        }
        flavor = conn.create_flavor(**flavor_prop)
        print(f"\t\tflavor {name} created")

    return flavor


def create_image(name=config.IMAGE_NAME, filename=config.SOURCE_CIRROS_IMAGE, min_disk=0, recreate=False):
    if 'cirros' in name:
        image = conn.image.find_image(config.IMAGE_STATE_NAME_CIRROS)
        if image:
            print(f"\timage based on cirros already exists")
            return image
    elif 'ubuntu' in name:
        image = conn.image.find_image(config.IMAGE_STATE_NAME_UBUNTU)
        if conn.image.find_image(config.IMAGE_STATE_NAME_UBUNTU):
            print(f"\timage based on ubuntu already exists")
            return image
        image = conn.image.find_image(config.IMAGE_STATE_NAME_UBUNTU2)
        if image:
            print(f"\timage based on ubuntu already exists")
            return image
    if recreate:
        for image in conn.image.images():
            if image.name == config.IMAGE_NAME:
                conn.image.delete_image(image)

    image = conn.image.find_image(name)

    if image:
        print(f"\timage {name} already exists")
    else:
        print(f"\tcreating image {name}")
        image = conn.create_image(
            name=name, filename=filename, min_disk=min_disk, wait=True, timeout=20)
        print(f"\t\timage {name} created")

    return image


def get_volume_list():
    for volume in conn.block_storage.volumes():
        print(volume)


def get_images_list():
    images_list = []
    for image in conn.image.images():
        print(image)
        images_list.append(image)
    return images_list


def check_for_exists_vm(name, image_name):

    try:
        server = conn.compute.find_server(name)
    except exceptions.DuplicateResource:
        remove_vms([name])
        return False

    if server:
        if server.status == "ACTIVE":
            if 'cirros' in image_name:
                os_name = 'cirros'
            else:
                os_name = 'ubuntu'
            print(f"attempt to stop an active screen session on {server.name}")

            run_command_on_vm_from_hv(server, os_name, f"screen -S {config.SCREEN_SESSION} -X quit")
            check_screen_session = run_command_on_vm_from_hv(server, os_name, f"screen -ls")
            if not ('No Sockets found' in check_screen_session):
                remove_vms([name])
                return False
            else:
                return True
        else:
            return False
    else:
        return False


def create_vm(
        name=config.SERVER_NAME,
        network_name=config.NETWORK_NAME,
        flavor_name=config.FLAVOR_NAME,
        image_name=config.IMAGE_NAME+'_cirros',
        volume_size=1,
        keypair=True,
        recreate=False,
        **attrs):
    print(f"Creating vm {name}")

    if recreate:
        for server in conn.compute.servers():
            if server.name == config.SERVER_NAME:
                conn.compute.delete_server(server)
                conn.compute.wait_for_delete(server, interval=2, wait=120)
                print(f"\tvm {name} deleted")

    server = check_for_exists_vm(name, image_name)

    if not server:  # or server_status != 'ACTIVE':
        flavor = create_flavor(name=flavor_name)
        image = create_image(name=image_name)
        security_group = create_security_group()
        network = create_network(name=network_name)

        server_prop = {
            'name': name,
            'flavor_id': flavor.id,
            'image_id': image.id,
            'security_groups': [security_group],
            'networks': [{"uuid": network.id}],
            'block_device_mapping': [{'source_type': 'image',
                                      'destination_type': 'volume',
                                      'volume_size': volume_size,
                                      'device_name': '/dev/sda',
                                      'boot_index': 0,
                                      "uuid": image.id,
                                      "delete_on_termination": True
                                      # 'guest_format': 'swap',
                                      # 'device_type': 'disk',
                                      # 'disk_bus': 'scsi',
                                      }],
            **attrs
        }

        if keypair:
            keypair = create_keypair()
            server_prop['key_name'] = keypair.name

        server = conn.compute.create_server(**server_prop)

        print(f"wait for Active status...")
        conn.compute.wait_for_server(server, status='ACTIVE', failures=None, interval=2, wait=120)
        print(f"vm {name} created\n--------------------------")
    else:
        print(f"vm {name} already exists\n--------------------------")


def batch_create_vm(name=config.SERVER_NAME,
                    network_name=config.NETWORK_NAME,
                    flavor_name=config.FLAVOR_NAME,
                    volume_size=1,
                    image_name=config.IMAGE_NAME+'_cirros',
                    keypair=True,
                    vm_qty=1):
    vms_name_list = []
    for i in range(vm_qty):
        new_name = name + str(i + 1)
        vms_name_list.append(new_name)
        create_vm(name=new_name,
                  network_name=network_name,
                  flavor_name=flavor_name,
                  volume_size=volume_size,
                  image_name=image_name,
                  keypair=keypair)

    return vms_name_list


def live_migrate_vm(migration_dict):
    for server_name, hv_name in migration_dict.items():
        print(f"start migrating {server_name} to {hv_name}")
        server = conn.compute.find_server(server_name)
        if server:
            if server.hypervisor_hostname != hv_name:
                conn.compute.live_migrate_server(server=server, host=hv_name)
                conn.compute.wait_for_server(server, status='MIGRATING', failures=None, interval=2, wait=120)
                conn.compute.wait_for_server(server, status='ACTIVE', failures=None, interval=2, wait=120)

                server = conn.compute.find_server(server_name)
                # print(server)
                if server and server.hypervisor_hostname == hv_name:
                    print(f"\tvm {server_name} running on {hv_name}")
                else:
                    print(f"\tvm {server_name} not migrate")
                    return False
            else:
                print(f"\tvm is already on this {hv_name}")
        else:
            print(f"\tvm {server_name} not found")
            return False
    return True


def wait_for_migrate(hv_list=None, expected_vms_on_host_1=0, expected_vms_on_host_2=0, cycles=0, cycle_duration=0):
    if not hv_list:
        return False
    print(f"wait {math.ceil(cycle_duration * cycles / 60)} min for migrate vm")
    for i in range(cycles):
        print(f"try for wait vm migrate to {hv_list[1].name} attempt {i}")
        vms_on_host_1 = get_vms_list_from_hv(hv_list[0].name)
        vms_on_host_2 = get_vms_list_from_hv(hv_list[1].name)
        print(f"on {hv_list[0].name}: {len(vms_on_host_1)} vms, "
              f"on {hv_list[1].name}: {len(vms_on_host_2)} vms")
        if len(vms_on_host_2) == expected_vms_on_host_2:
            print(f"server status: {vms_on_host_2[0].name} migrate on host: {vms_on_host_2[0].hypervisor_hostname}"
                  f" - OK!")
            return True
        time.sleep(cycle_duration)
    return False


def wait_for_remigrate(hv_list=None, expected_vms_on_host_1=0, expected_vms_on_host_2=0, cycles=0, cycle_duration=0):
    if not hv_list:
        return False
    print(f"wait {math.ceil(cycle_duration * cycles / 60)} min to make sure that there will be no re-migration")
    for i in range(cycles):
        print(f"try for wait vm migrate attempt {i}")
        vms_on_host_1 = get_vms_list_from_hv(hv_list[0].name)
        vms_on_host_2 = get_vms_list_from_hv(hv_list[1].name)
        print(f"on {hv_list[0].name}: {len(vms_on_host_1)} vms, "
              f"on {hv_list[1].name}: {len(vms_on_host_2)} vms")
        for vm in vms_on_host_1 + vms_on_host_2:
            if vm.status == 'MIGRATING':
                print(f"an unexpected migration {vm.name} - fail")
                return False
        if len(vms_on_host_1) != expected_vms_on_host_1 or len(vms_on_host_2) != expected_vms_on_host_2:
            print(f"an unexpected migration occurred - fail")
            return False
        time.sleep(cycle_duration)
    return True


def get_servers(find_vm_list='all'):
    # print(f"get servers...")
    servers_list = []
    if find_vm_list == 'all':
        for server in conn.compute.servers():
            servers_list.append(server)
    else:
        for server in conn.compute.servers():
            if server.name in find_vm_list:
                servers_list.append(server)

    return servers_list


def get_active_servers():
    servers_list = []
    servers = get_servers()
    # print(servers)
    for server in get_servers():
        # print(server)
        # print(server.status)
        if server.status == 'ACTIVE':
            servers_list.append(server)
    return servers_list


def get_host_infra_by_ip(host_ip):
    return testinfra.get_host(f"paramiko://root@{host_ip}")


def get_hv_and_vm_ip_from_server(server):
    host_name = server.hypervisor_hostname
    host = conn.compute.find_hypervisor(host_name)
    print(f"\t{server.addresses}")
    # {'pub_net': [{'version': 4, 'addr': '10.100.100.30', 'OS-EXT-IPS:type': 'fixed', 'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:06:3b:ab'}]}
    k = config.NETWORK_NAME
    for k, v in server.addresses.items():
        if k == config.NETWORK_STATE_NAME:
            vm_ip = server.addresses[k][0]['addr']
            return host, vm_ip
    vm_ip = server.addresses[k][0]['addr']
    return host, vm_ip


def get_own(host):
    cmpt_host_infra = get_host_infra_by_ip(host.host_ip)
    check_key = cmpt_host_infra.run(f"ls -f ./{config.KEYPAIR_FILE}")
    print(check_key.stderr)

    if check_key.stderr:
        print(f"\texecuting command: scp {config.INIT_FOLDER}{config.KEYPAIR_FILE} root@{host.host_ip}:~/")
        copy_key_to_cmpt = lcm_host_infra.check_output(
            f"scp {config.INIT_FOLDER}{config.KEYPAIR_FILE} root@{host.host_ip}:~/")
        print(copy_key_to_cmpt)
        print(f"\texecuting command: chmod 400 ./{config.KEYPAIR_FILE}")
        cmpt_host_infra.check_output(f"chmod 400 ./{config.KEYPAIR_FILE}")

    cmd_own = cmpt_host_infra.run("rm -f .ssh/known_hosts & export OWN=$(ip netns | awk '{print $1}') ; echo $OWN")
    own = cmd_own.stdout.replace('\n', '')
    print(f"\t{own}")
    return own


def copy_from_lcm_to_nodes(hypervisor, file_name):
    if hypervisor:
        print(lcm_host_infra.check_output(
            f"scp {config.INIT_FOLDER}{file_name} root@{hypervisor.host_ip}:~/"))
        return True
    else:
        return False


def copy_stress_and_screen_to_hv(hypervisors):
    if hypervisors:
        print(f"copy stress, screen to compute nodes from lcm...")
        for hv in hypervisors:
            lcm_host_infra.check_output(
                f"scp {config.INIT_FOLDER}{config.STRESS_FILE} root@{hv.host_ip}:~/")
            # lcm_host_infra.check_output(
            #     f"scp {config.INIT_FOLDER}{config.KEYPAIR_FILE} root@{hv.host_ip}:~/")
            # lcm_host_infra.check_output(
            #     f"ssh root@{hv.host_ip} chmod 400 ./{config.KEYPAIR_FILE}")
            lcm_host_infra.check_output(
                f"scp {config.INIT_FOLDER}{config.SCREEN_CENTOS_DEB_FILE} root@{hv.host_ip}:~/")
        return True


def copy_file_to_vm_from_hv(server, vm_os_name, source_file, destination):
    print(f"\tcopying {source_file} to {server.name}")
    host, vm_ip = get_hv_and_vm_ip_from_server(server)

    if host:
        own = get_own(host)
        if not own:
            return False
        for n in range(5):
            cmd_copy = (f"ip netns exec {own} scp -o \"StrictHostKeyChecking=no\" "
                        f"-i ./{config.KEYPAIR_FILE} ./{source_file} {vm_os_name}@{vm_ip}:{destination}")
            print(f"\texecuting command: {cmd_copy}")
            cmpt_host_infra = get_host_infra_by_ip(host.host_ip)
            cmd_on_vm = cmpt_host_infra.run(cmd_copy)
            print(cmd_on_vm.stdout, cmd_on_vm.stderr)
            cmd_check_file = cmpt_host_infra.run(f"ip netns exec {own} ssh -o \"StrictHostKeyChecking=no\""
                                                 f" -i ./{config.KEYPAIR_FILE} {vm_os_name}@{vm_ip}"
                                                 f" ls -f /home/{vm_os_name}/{source_file}")
            if not cmd_check_file.stderr:
                print(f"\t{source_file} was coped")
                return True
            time.sleep(5)
        return False
    else:
        print(f"Hypervisor {host.name} not found")
        return False


def copy_file_to_vms_from_hv(vm_list, vm_os_name, source, destination):
    print(f"Copying files to vms")
    vm_list_for_copy = get_servers(vm_list)
    # print(vm_list_for_copy)
    for vm in vm_list_for_copy:
        if not copy_file_to_vm_from_hv(vm, vm_os_name, source, destination):
            return False
    return True


def run_command_on_lcm(cmd):
    print(lcm_host_infra.check_output(cmd))
    return True


def run_command_on_node(node, cmd):
    print(lcm_host_infra.check_output(f"ssh -t -o StrictHostKeyChecking=no {node.host_ip} {cmd}"))
    return True


# (maybe change to check_output)
def run_command_on_vm_from_hv(server, vm_os_name, command):
    if not command:
        return False
    print(f"\texecute command: {command} on {server.name}")
    host, vm_ip = get_hv_and_vm_ip_from_server(server)

    if host:
        cmpt_host_infra = get_host_infra_by_ip(host.host_ip)
        own = get_own(host)

        cmd_string = (f"ip netns exec {own} ssh -o \"StrictHostKeyChecking=no\" "
                      f"-i test_key.pem {vm_os_name}@{vm_ip} {command}")
        print(cmd_string)
        cmd_on_vm = cmpt_host_infra.run(cmd_string)
        print(cmd_on_vm.stdout)
        if cmd_on_vm.stdout:
            return cmd_on_vm.stdout
        print(f"\tcommand: {command} was executed from {host.name}")
        return True
    else:
        print(f"Hypervisor {host.name} not found")
        return False


# Running the same commands on different VMs of the same hv
def run_cmd_on_multiple_vms(qty_commands_dict, vm_os_name, command):
    print('Running command on vms')
    vms_with_processes_list = []
    for host_name, qty_stress in qty_commands_dict.items():
        host = conn.compute.find_hypervisor(host_name)
        if host:
            vm_list = []
            for server in conn.compute.servers():
                # print(server.compute_host)
                if server.compute_host == host_name:
                    vm_list.append(server)
            # print(vm_list)

            if len(vm_list) >= qty_stress:
                for i in range(qty_stress):
                    # command = '\"ls -la\"'
                    run_command_on_vm_from_hv(vm_list[i], vm_os_name, command)
                    vms_with_processes_list.append(vm_list[i])
            else:
                print(f"not enough vms on compute: {host_name} to run {qty_stress} processes")

    return vms_with_processes_list


# Running the different commands on different VMs
# example: commands_dict = {'vm_name1': ('os_name','command'), 'vm_name2': ('os_name','command') ...}
def run_diff_cmd_on_multiple_vms(commands_dict):
    print('Running the different commands command on vms')
    for vm_name, command in commands_dict.items():
        try:
            server = conn.compute.find_server(vm_name)
        except exceptions.DuplicateResource:
            print(f"more than one vm with the same name: {vm_name}")
            return False

        if server:
            run_command = run_command_on_vm_from_hv(server, *command)
            if not run_command:
                return False
    return True


def stop_processes_on_vms(vms_list, vm_os_name, command):
    print('Stop processes on vms')
    for vm in vms_list:
        run_command_on_vm_from_hv(vm, vm_os_name, command)
        print(f'\tstop process on {vm.name}')
    print('Stopping processes on vms was finishing')


# Install screen on vm (maybe check before install)
def install_screen_on_all_vms():
    for server in conn.compute.servers():
        run_command_on_vm_from_hv(server, 'ubuntu', config.INSTALL_SCREEN_COMMAND)


def disable_network_on_host(host):
    print(host)
    print(f"check for script {config.DISABLE_NETWORK_SCRIPT}")
    if host.run(f"ls -f ./{config.DISABLE_NETWORK_SCRIPT}").stderr:
        print(f"upload {config.DISABLE_NETWORK_SCRIPT}...")
        cmd_upload_dis_net_script = lcm_host_infra.run(f"scp {config.INIT_FOLDER}{config.DISABLE_NETWORK_SCRIPT}"
                                                       f" 10.0.0.21:~/")
        print(cmd_upload_dis_net_script.stdout, cmd_upload_dis_net_script.stderr)
        if cmd_upload_dis_net_script.stderr:
            return False
    print(f"check screen...")
    cmd_check_screen = host.run(f"rpm -qa | grep -E 'screen'")
    if cmd_check_screen.stdout == "":
        print(f"install screen...")
        if host.run(f"ls -f ./{config.SCREEN_CENTOS_DEB_FILE}").stderr:
            print(f"\tupload {config.SCREEN_CENTOS_DEB_FILE}...")
            cmd_upload_screen = lcm_host_infra.run(f"scp {config.INIT_FOLDER}{config.SCREEN_CENTOS_DEB_FILE} 10.0.0.21:~/")
            print(cmd_upload_screen.stdout, cmd_upload_screen.stderr)
            if cmd_upload_screen.stderr:
                return False
            cmd_install_screen = host.run(f"yum install -y ./{config.SCREEN_CENTOS_DEB_FILE}")
            print(cmd_install_screen.stdout, cmd_install_screen.stderr)
            if cmd_install_screen.stderr:
                return False
    cmd_start_disable_network = host.run(f"screen -d -m bash {config.DISABLE_NETWORK_SCRIPT}")
    print(cmd_start_disable_network.stdout, cmd_start_disable_network.stderr)
    return True


def remove_vms(name_list):
    print('removing vms')
    for server in conn.compute.servers():
        if server.name in name_list:
            # print(dir(server))
            # print(dir(server.attached_volumes[0]))
            # print(server.attached_volumes[0].id)
            # volume_id = server.attached_volumes[0].id
            conn.compute.delete_server(server)
            conn.compute.wait_for_delete(server, interval=2, wait=120)
            # remove_volumes([volume_id])
            print(f"vm {server.name} was removed")


def remove_volumes(id_list):
    if id_list:
        for volume in conn.block_storage.volumes():
            if volume.id in id_list:
                conn.block_storage.delete_volume(volume)
                conn.block_storage.wait_for_delete(volume, interval=2, wait=120)
                print(f"volume {volume.name} was removed")


def remove_security_groups(name_list):
    print('removing ports')
    for port in conn.network.security_groups():
        if port.name in name_list:
            conn.network.delete_security_group(port)
            print(f" port {port.name} was removed")


def remove_routers(name_list):
    print('removing routers')
    for router in conn.network.routers():
        if router.name in name_list:
            conn.network.delete_router(router)
            print(f" router {router.name} was removed")


def remove_network(name_list):
    print('removing networks')
    for network in conn.network.networks():
        if network.name in name_list:
            conn.network.delete_network(network)
            print(f"\tnetwork {network.name} was removed")


def remove_keypair(name_list):
    print('removing keypairs')
    for keypair in conn.compute.keypairs():
        if keypair.name in name_list:
            conn.compute.delete_keypair(keypair)
            print(f"\tkeypair: {keypair.name} was removed")


def remove_images(name_list):
    print('removing images')
    for image in conn.image.images():
        if image.name in name_list:
            conn.image.delete_image(image)
            print(f"\timage: {image.name} was removed")


def remove_flavors(name_list):
    print('removing flavors')
    for flavor in conn.compute.flavors():
        if flavor.name in name_list:
            conn.compute.delete_flavor(flavor)
            print(f"\tflavor: {flavor.name} was removed")


def remove_resources(remove_list):
    print(f"removing list: {remove_list}")
    # remove vm
    if any(x in ['servers', 'all'] for x in remove_list):
        print('removing vm')
        for server in conn.compute.servers():
            conn.compute.delete_server(server)
            conn.compute.wait_for_delete(server, interval=2, wait=120)
            print(f"\tvm {server.name} was removed")
    # remove routers
    if any(x in ['routers', 'all'] for x in remove_list):
        print('removing routers')
        for router in conn.network.routers():
            conn.network.delete_router(router)
            print(f"\trouter {router.name} was removed")
    # remover security groups
    if any(x in ['ports', 'all'] for x in remove_list):
        print('removing ports')
        for port in conn.network.security_groups():
            print(f"\tsec_group: {port.id}, {port.name}")
            # if not (port.name in ['default', 'lb-mgmt-sec-grp', 'lb-health-mgr-sec-grp']):
            #     conn.network.delete_security_group(port)
            #     print(f"\tsec_group: {port.id} was removed")
            conn.network.delete_security_group(port.id)
            print(f"\tsec_group: {port.id} was removed")

    # remove networks
    if any(x in ['networks', 'all'] for x in remove_list):
        print('removing networks')
        for network in conn.network.networks():
            # if not (network.name in ['lb-mgmt-net']):
            conn.network.delete_network(network.id)
            print(f"\tnetwork {network.id} was removed")
    # remove keypairs
    if any(x in ['keypairs', 'all'] for x in remove_list):
        print('removing keypairs')
        for keypair in conn.compute.keypairs():
            conn.compute.delete_keypair(keypair)
            print(f"\tkeypair: {keypair.name} was removed")
    # remove image
    if any(x in ['images', 'all'] for x in remove_list):
        print('removing images')
        for image in conn.image.images():
            conn.image.delete_image(image)
            print(f"\timage: {image.name} was removed")
    # remove flavors
    if any(x in ['flavors', 'all'] for x in remove_list):
        print('removing flavors')
        for flavor in conn.compute.flavors():
            if not (flavor.name in ['amphora']):
                conn.compute.delete_flavor(flavor)
                print(f"\tflavor: {flavor.name} was removed")
    # remove volumes
    if any(x in ['volumes', 'all'] for x in remove_list):
        print('removing volumes')
        for volume in conn.block_storage.volumes():
            conn.block_storage.delete_volume(volume)  # , wait=120)  # interval=2,
            print(f"\tvolume: {volume.id} was removed")
