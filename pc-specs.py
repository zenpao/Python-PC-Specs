from datetime import datetime
import socket
import uuid
import psutil
import platform
import cpuinfo
import wmi
import GPUtil

def get_system_info():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    c = wmi.WMI()
    system = c.Win32_ComputerSystem()[0]
    bios = c.Win32_BIOS()[0]
    os_info = platform.uname()

    computer_name = socket.gethostname()
    manufacturer = system.Manufacturer.strip()
    model = system.Model.strip()
    serial_number = bios.SerialNumber.strip()
    manufactured_year = int(bios.ReleaseDate[:4])
    current_year = now.year
    system_age = current_year - manufactured_year

    os_name = os_info.system
    os_version = os_info.version

    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(40, -8, -8)])

    ipv4_addresses = []
    ipv6_addresses = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:
                ipv4_addresses.append(f"  - {interface_name}: {address.address}")
            elif address.family == socket.AF_INET6:
                ipv6_addresses.append(f"  - {interface_name}: {address.address}")

    svmem = psutil.virtual_memory()
    total_ram = round(svmem.total / (1024 ** 3), 2)
    available_ram = round(svmem.available / (1024 ** 3), 2)
    used_ram = round(total_ram - available_ram, 2)
    ram_percent = svmem.percent

    net_io = psutil.net_io_counters()
    bytes_sent = round(net_io.bytes_sent / (1024 ** 2), 2)
    bytes_recv = round(net_io.bytes_recv / (1024 ** 2), 2)

    try:
        gpus = GPUtil.getGPUs()
        gpu = gpus[0].name if gpus else "N/A"
    except:
        gpu = "N/A"

    try:
        cpu_data = cpuinfo.get_cpu_info()
        raw_name = cpu_data.get("brand_raw", "N/A")
        identifier = cpu_data.get("arch_string_raw", "N/A")
        processor = f"{identifier} ({raw_name})" if raw_name != "N/A" else identifier
    except:
        processor = "N/A (N/A)"

    report = f"""Computer Name: {computer_name}
Manufacturer: {manufacturer}
Model: {model}
Serial Number: {serial_number}
Manufactured Year: {manufactured_year}
System Age (Years): {system_age}
OS: {os_name}
OS Version: {os_version}
Processor: {processor}
GPU: {gpu}

MAC Address: {mac_address}

IPv4 Addresses:
{chr(10).join(ipv4_addresses)}

IPv6 Addresses:
{chr(10).join(ipv6_addresses)}

RAM Info:
  Total RAM: {total_ram} GB
  Available RAM: {available_ram} GB
  Used RAM: {used_ram} GB
  RAM Usage (%): {ram_percent}%

Network Usage:
  Bytes Sent: {bytes_sent} MB
  Bytes Received: {bytes_recv} MB
"""

    filename = f"{date_str}_PC_{computer_name}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(report)

    print(report)
    input(f"\nReport saved as '{filename}'. Press Enter to exit...")

get_system_info()
