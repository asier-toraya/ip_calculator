# IP Calculator Script

This Python script provides a graphical user interface (GUI) tool to perform IP network calculations. It allows users to input an IP address with a subnet mask (in CIDR notation) and calculates the following:

- **Network Address**: The base address of the network.
- **Subnet Mask**: The mask defining the network portion of the IP.
- **Broadcast Address**: The last address in the subnet used for broadcasting.
- **Binary Representation**: The binary format of the network address.

Additionally, the script offers two advanced subnetting features:

1. **Subnet Creation by Number of Subnets**:  
   Users can specify how many subnets they want to create from the given network. The script calculates and displays the network address, subnet mask, and broadcast address for each of the requested subnets.

2. **Subnet Creation by Number of Devices**:  
   Users can input one or multiple device counts (comma-separated) to create subnets sized appropriately for each number of devices. The script uses Variable Length Subnet Masking (VLSM) to allocate subnets efficiently, calculating the smallest subnet that fits each device count, and displays the corresponding network address, mask, and broadcast address.

The GUI is designed to be user-friendly and clear, with separate sections for each calculation type and easy-to-read output areas.

## Usage

- Enter an IP address with mask (e.g., `192.168.1.10/24`) and click **Calcular** to see the main network details.
- Enter the number of subnets you want to create and click **Calcular** to see the subnet details.
- Enter one or more device counts separated by commas (e.g., `1000,200,50`) and click **Calcular** to see the VLSM subnet allocations.

This tool is useful for network administrators and students learning about IP subnetting and network design.

---
To start the script, run the following command in your terminal:

```bash
python ip_calc.py
```

You can create a shortcut to the script by creating a batch file with the following content:

```batch
@echo off
python "C:\Path\To\ip_calc.py"
```

Replace `"C:\Path\To\ip_calc.py"` with the actual path to the script.