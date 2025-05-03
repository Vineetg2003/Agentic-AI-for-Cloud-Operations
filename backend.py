import os
from dotenv import load_dotenv
from openstack import connection
from openstack.exceptions import ResourceNotFound, OpenStackCloudException
from agent3 import chain  # Make sure agent3.chain returns result with .intent and .entities

load_dotenv()

def initialize_openstack():
    """Initialize OpenStack connection with AceCloud endpoints."""
    try:
        required_vars = [
            "OS_AUTH_URL", "OS_PROJECT_ID", "OS_USERNAME",
            "OS_PASSWORD", "OS_REGION_NAME"
        ]
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Environment variable {var} is not set")

        service_endpoints = {
            "compute": "https://api-ap-south-mum-1.openstack.acecloudhosting.com:8774/v2.1",
            "network": "https://api-ap-south-mum-1.openstack.acecloudhosting.com:9696",
            "volumev3": "https://api-ap-south-mum-1.openstack.acecloudhosting.com:8776/v3/a02b14bcfca64e44bd68f2d00d8555b5",
            "identity": "https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000",
            "image": "https://api-ap-south-mum-1.openstack.acecloudhosting.com:9292"
        }

        conn = connection.Connection(
            auth_url=os.getenv("OS_AUTH_URL"),
            project_id=os.getenv("OS_PROJECT_ID"),
            username=os.getenv("OS_USERNAME"),
            password=os.getenv("OS_PASSWORD"),
            user_domain_name=os.getenv("OS_USER_DOMAIN_NAME", "Default"),
            project_domain_name=os.getenv("OS_PROJECT_DOMAIN_NAME", "Default"),
            region_name=os.getenv("OS_REGION_NAME")
        )
        return conn
    except Exception as e:
        raise Exception(f"Failed to initialize OpenStack connection: {e}")

def execute_openstack_action(conn, intent, entities):
    """Execute OpenStack actions based on intent and entities."""
    DEFAULT_NETWORK = "abc"  # Replace with your real network name
    confirm_required = [
        "create_vm", "resize_vm", "delete_vm",
        "create_network", "create_volume", "delete_volume"
    ]

    if intent in confirm_required:
        print(f"Executing {intent} with entities: {entities}")
        confirmation = input("Confirm action (Yes/No): ").strip().lower()
        if confirmation != "yes":
            print("Action cancelled by user.")
            return False

    try:
        if intent == "create_vm":
            name = entities.get("name")
            flavor = entities.get("flavor")
            volume_name = entities.get("volume_name", f"{name}-boot")
            if not name or not flavor:
                raise ValueError("Missing name or flavor for create_vm")
            flavor_obj = conn.compute.find_flavor(flavor)
            if not flavor_obj:
                raise ValueError(f"Flavor {flavor} not found")
            network_obj = conn.network.find_network(DEFAULT_NETWORK)
            if not network_obj:
                raise ValueError(f"Network {DEFAULT_NETWORK} not found")
            volume = conn.block_storage.find_volume(volume_name)
            if not volume:
                raise ValueError(f"Volume {volume_name} not found")
            if not volume.is_bootable:
                raise ValueError(f"Volume {volume_name} is not bootable")

            server = conn.compute.create_server(
                name=name,
                flavorRef=flavor_obj.id,
                networks=[{"uuid": network_obj.id}],
                block_device_mapping_v2=[{
                    "uuid": volume.id,
                    "source_type": "volume",
                    "destination_type": "volume",
                    "boot_index": 0,
                    "delete_on_termination": True
                }]
            )
            print(f"VM {name} created successfully with volume {volume_name}.")
            return True

        elif intent == "resize_vm":
            name = entities.get("name")
            flavor = entities.get("flavor")
            if not name or not flavor:
                raise ValueError("Missing name or flavor for resize_vm")
            server = conn.compute.find_server(name)
            flavor_obj = conn.compute.find_flavor(flavor)
            if not server or not flavor_obj:
                raise ValueError(f"Server {name} or flavor {flavor} not found")
            conn.compute.resize_server(server=server.id, flavor=flavor_obj.id)
            print(f"VM {name} resized to flavor {flavor} successfully.")
            return True

        elif intent == "delete_vm":
            name = entities.get("name")
            if not name:
                raise ValueError("Missing name for delete_vm")
            server = conn.compute.find_server(name)
            if not server:
                raise ValueError(f"Server {name} not found")
            conn.compute.delete_server(server.id)
            print(f"VM {name} deleted successfully.")
            return True

        elif intent == "create_network":
            name = entities.get("name")
            if not name:
                raise ValueError("Missing name for create_network")
            network = conn.network.create_network(name=name)
            subnet = conn.network.create_subnet(
                name=f"{name}-subnet",
                network_id=network.id,
                ip_version=4,
                cidr="10.0.0.0/24",
                gateway_ip="10.0.0.1",
                allocation_pools=[{"start": "10.0.0.100", "end": "10.0.0.200"}],
                dns_nameservers=["8.8.8.8", "8.8.4.4"]
            )
            print(f"Network {name} and subnet {subnet.name} created successfully.")
            return True

        elif intent == "create_volume":
            name = entities.get("name")
            size = entities.get("size")
            image_id = entities.get("image_id")
            if not name or not size:
                raise ValueError("Missing name or size for create_volume")
            if not image_id:
                raise ValueError("Missing image_id for bootable volume")
            image = conn.image.find_image(image_id)
            if not image:
                raise ValueError(f"Image {image_id} not found")
            volume = conn.block_storage.create_volume(
                name=name,
                size=int(size),
                imageRef=image_id,
                bootable=True
            )
            print(f"Bootable volume {name} ({size} GB) created successfully with image {image_id}.")
            return True

        elif intent == "delete_volume":
            name = entities.get("name")
            if not name:
                raise ValueError("Missing name for delete_volume")
            volume = conn.block_storage.find_volume(name)
            if not volume:
                raise ValueError(f"Volume {name} not found")
            conn.block_storage.delete_volume(volume.id)
            print(f"Volume {name} deleted successfully.")
            return True

        elif intent == "get_usage":
            limits = conn.compute.get_limits()
            print("Project Usage:")
            print(f"Max Total Cores: {limits.max_total_cores}")
            print(f"Max Total RAM (MB): {limits.max_total_ram}")
            print(f"Max Total Instances: {limits.max_total_instances}")
            return True

        else:
            print(f"Unknown intent: {intent}")
            return False

    except ResourceNotFound as e:
        print(f"Resource not found: {e}")
        return False
    except OpenStackCloudException as e:
        print(f"OpenStack error: {e}")
        return False
    except ValueError as e:
        print(f"Validation error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    """Main loop to process user requests."""
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set in .env file")
    
    conn = initialize_openstack()

    while True:
        user_input = input("Enter your request (or 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            break
        try:
            result = chain.invoke({"input": user_input})
            intent = result.get("intent")
            entities = result.get("entities")
            print(f"Parsed Intent: {intent}")
            print(f"Parsed Entities: {entities}")
            success = execute_openstack_action(conn, intent, entities)
            if success:
                print("Action completed successfully.")
            else:
                print("Action failed.")
        except Exception as e:
            print(f"Error processing request: {e}")
        print("-" * 50)

# 🔧 Critical Fix: This was written incorrectly
if __name__ == "__main__":
    main()
