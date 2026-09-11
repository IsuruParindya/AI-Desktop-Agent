import json
import platform
import subprocess


def get_system_info(args: dict, **kwargs) -> str:
    """Get hardware, operating system, and storage information from the Windows PC."""

    powershell_script = r"""
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors
$computer = Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
$gpus = @(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name)
$drives = @(Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" |
    Select-Object DeviceID,VolumeName,Size,FreeSpace)

$result = [PSCustomObject]@{
    CPU = $cpu
    RAMBytes = $computer.TotalPhysicalMemory
    GPUs = $gpus
    Drives = $drives
}

$result | ConvertTo-Json -Depth 5 -Compress
"""

    try:
        output = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                powershell_script,
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )

        hardware = json.loads(output)

    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
    ):
        hardware = {}

    # Operating system
    os_name = platform.system()
    os_release = platform.release()
    os_version = platform.version()
    architecture = platform.machine()
    hostname = platform.node()

    # CPU
    cpu_data = hardware.get("CPU") or {}

    if isinstance(cpu_data, list):
        cpu_data = cpu_data[0] if cpu_data else {}

    cpu_name = cpu_data.get("Name") or platform.processor()

    cpu_cores = cpu_data.get("NumberOfCores")
    logical_processors = cpu_data.get("NumberOfLogicalProcessors")

    # RAM
    ram_bytes = hardware.get("RAMBytes")

    if ram_bytes:
        ram_gb = round(int(ram_bytes) / (1024 ** 3), 2)
    else:
        ram_gb = None

    # GPU
    gpus = hardware.get("GPUs") or []

    if isinstance(gpus, str):
        gpus = [gpus]

    # Storage
    drives = hardware.get("Drives") or []

    if isinstance(drives, dict):
        drives = [drives]

    storage = []

    for drive in drives:
        if not isinstance(drive, dict):
            continue

        device = drive.get("DeviceID")
        volume_name = drive.get("VolumeName")

        size = drive.get("Size")
        free_space = drive.get("FreeSpace")

        if size:
            size_gb = round(int(size) / (1024 ** 3), 2)
        else:
            size_gb = None

        if free_space:
            free_gb = round(int(free_space) / (1024 ** 3), 2)
        else:
            free_gb = None

        if size and free_space:
            used_gb = round(
                (int(size) - int(free_space)) / (1024 ** 3),
                2,
            )
        else:
            used_gb = None

        storage.append(
            {
                "drive": device,
                "label": volume_name,
                "total_gb": size_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
            }
        )

    result = {
        "hostname": hostname,
        "operating_system": os_name,
        "windows_release": os_release,
        "windows_version": os_version,
        "architecture": architecture,
        "cpu": cpu_name,
        "cpu_cores": cpu_cores,
        "cpu_logical_processors": logical_processors,
        "ram_gb": ram_gb,
        "gpu": gpus,
        "storage": storage,
    }

    return json.dumps(result)