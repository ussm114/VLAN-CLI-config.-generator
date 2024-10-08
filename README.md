# VLAN-CLI-config.-generator
## Key points
Generates CLI commmands for VLAN configuration of switches in Collapsed-Core network architecture.  
Advantages:  
Bandwidth saving: Only relevant traffic is exchanged between switches: if a VLAN isn't used outside an access switch, its traffic will not be sent by trunk.  
Semi-automatic work: speeds up the configuration stage.
## Usage
Use `py "generate vlan.py"`.  
  
![Usage](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/usage.png?raw=true "Usage")
### Input
Configured spreadsheet "vlan config - data.ods", helper file "template.ods" 
![Tables with data to configure](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/tables.png?raw=true "Tables")
The cell must contain:  
- a number: to specify which VLAN to assign an Interface traffic to;
- a device name: to specify which device the Interface connects to.
> [!NOTE]
> Currently only supported architecture is Collapsed-Core.
> There can be 1 Core switch, and many Access switches.
### Output
Text files with CLI commands:  
![generated files](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/generated%20files.png?raw=true "generated files")
## Test
Results: VLANs work correctly, traffic is properly organized: PCs on the same VLAN can communicate, PCs on different VLANs can't.
### Architecture
Tests were conducted on following network in Cisco Packet Tracer:
![Simulated network](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/network%20architecture.png?raw=true "Simulated network")
### Hosts setup
Host number is its last octet of IP. Example of PC14 with IP .14:
![Host setup](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/host%20setup%20-%20example%20PC14.png?raw=true "Host setup")
### Configuring the switches
Paste the generated commands in CLI. Results photos (before on the left, after on the right) :  
The VLANs get added to switch database:
![WS-A2 VLAN configuration](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/example%20conf%20ws-a2%20vlan%20before%20after.png?raw=true "WS-A2 VLAN configuration")  
  
The iterface gets assigned to a VLAN:
![WS-A2 interface configuration](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/example%20conf%20ws-a2%20interface%20before%20after.png?raw=true "WS-A2 interface configuration")
### Test case #1: check ping response from PCs on same VLAN (within same Access switch), and on different VLAN.
#### #1a: Checked by ping from PC1
Result: After adding VLANs, the PC12 and PC22 become unavailable.     
Results of ping from PC1 (192.168.1.1):
![Results of ping from PC1 (192.168.1.1)](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/test1a%20PC1%20summary.png?raw=true "Results of ping from PC1 (192.168.1.1)")
This shows correct operation of VLANs - limiting of broadcast range.
#### #1b: Checked by ping from PC11
Result:  
 - without VLANs: all PCs reply to ping;  
 - with VLANs   : only PC12 replies to ping.  
Result: This confirms correct operation of Switches with configured VLANs - PCs on different VLAN become unreachable.
Results of ping from PC11 (192.168.1.11):
![Results of ping from PC11 (192.168.1.11)](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/test1b%20PC11%20summary.png?raw=true "Results of ping from PC11 (192.168.1.11)")
### Test case #2: check ping response from PC on same and on different VLAN, in whole network.
Checked by ping from PC21.
Result:
 - without VLANs: all PCs reply to ping;
 - with VLANs 	: only PCs from VLAN 30 reply to ping.
Results of ping from PC21 (192.168.1.21):
![Results of ping from PC11 (192.168.1.11)](https://github.com/ussm114/VLAN-CLI-config.-generator/blob/main/photos/test2%20PC21%20summary.png?raw=true "Results of ping from PC21 (192.168.1.21)")
PC13 is on different Access Switch than PC21 (WS-A2 and WS-A3 respectively).
The communication with PC13 is working correctly with VLANs, so the proper operation of Core switch is also confirmed.  
### Conclusion
The script operates correctly: generates proper commands for Core and Access - so that the PCs on the same VLAN can communicate, the PCs on different VLANs can't.
## Clarification
I wrote and tested the program myself, without generative AI tools.
