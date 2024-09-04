def add_vlan_to_core_trunk(df, access, vlan):
    df.iloc[df["vlan ID"] == vlan, df.columns.get_loc(C_to_A_ifs[access])] = "Tagged"

def add_vlan_to_access_trunk(df, access, vlan):
    df.iloc[df["vlan ID"] == vlan, df.columns.get_loc(A_to_C_ifs[access])] = "Tagged"

def add_untag_to_access_trunk(df, interface, vlan):
    df.iloc[df["vlan ID"] == vlan, df.columns.get_loc(interface)] = "A"

def read_df(file, sheet):
    df = pd.read_excel(file, sheet_name=sheet, engine="odf") #df = df.astype(str)
    return df
    
def unique_vlans(df):
    vlans_raw = df["vlan ID"].to_list()
    vlans_ints = []
    for x in vlans_raw:
        if isinstance(x, int):
            vlans_ints.append(x)
        # as is, automatically skips non-int x's
    vlans_unique = np.unique(vlans_ints).tolist()
    vlans = np.array(vlans_unique, dtype=int)  #convert to int. not sooner bc there was strings: "-" etc
    return vlans

import pandas as pd
import numpy as np

#read sheet: if
c_sw = "WS-C1"
df_core = pd.read_excel("vlan config - data.ods", sheet_name=c_sw+" Interf.", engine="odf")
mask = df_core['Dev'] == "-"
df_if = df_core[~mask]
Acc_Sw, All_Sw = df_if["Dev"].to_list(), df_if["Dev"].to_list()
All_Sw.append(c_sw)
C_to_A_ifs = df_if["Intf"].to_list()

#read input sheet: accesses
file = "vlan config - data.ods"
dfs = {sw: read_df(file, sw) for sw in Acc_Sw}

#read "out" sheet (for vlan export)
dfs_out = {sw: read_df("template.ods", "WS-C | A") for sw in All_Sw} 

# make list: which Access interface links to Core SW (for trunk)
A_to_C_ifs = []  
for i in range(len(Acc_Sw)):
    rows, _cols = dfs[Acc_Sw[i]].shape
    for r in range(rows) :
        #print(f"{i=}, {r=}, {Acc_Sw[i]=}, type={type(dfs[Acc_Sw[i]].iloc[r,1])}")
        if isinstance(dfs[Acc_Sw[i]].iloc[r,1], int):
            continue
        if "WS" in dfs[Acc_Sw[i]].iloc[r,1]:
            x = dfs[Acc_Sw[i]].iloc[r,0]
            A_to_C_ifs.append(x)
            break

#put Access vlans to df_out
for a_i, a in enumerate(Acc_Sw):
    df = dfs[a]
    rows, _cols = df.shape
    for r in range(rows):
        x = df.iloc[r,1]
        if isinstance(x, str): #(x == "-") or ("WS" in x):
            continue
        if isinstance(x, int):
            add_untag_to_access_trunk(dfs_out[a], df.iloc[r,0], x)

#_unique VLANs
Access_vlans = []
for a in Acc_Sw:
    Access_vlans.append(unique_vlans(dfs[a]))
    
#_unique VLANs
vlans_uniq = []
for sw in Acc_Sw:
    vlans_uniq.append(unique_vlans(dfs[sw]))
vlans_uniq.append(unique_vlans(dfs_out[c_sw]))
All_vlans_dict = {All_Sw[i]: vlans_uniq[i] for i in range(len(All_Sw))} 
 
# trunk vlans: write "Tagged" to proper dataframes
A_cnt = len(Access_vlans) #a = 1 access switch. A = All access switches. A_cnt = count of access switches
for a in range(0, A_cnt - 1): 
    for a2 in range(a + 1, A_cnt):
        for v in Access_vlans[a]:
            for v2 in Access_vlans[a2]:
                if v == v2:
                    #print(f"VLAN {v} is duplicated in 'i-f' {a=} and {a2=}")
                    add_vlan_to_core_trunk(dfs_out[c_sw], a, v)
                    add_vlan_to_core_trunk(dfs_out[c_sw], a2, v2)
                    add_vlan_to_access_trunk(dfs_out[Acc_Sw[a]], a, v)
                    add_vlan_to_access_trunk(dfs_out[Acc_Sw[a2]], a2, v2)

#export VLAN Table (T/A/"") to spreadsheets
dfs_out[c_sw].to_excel(c_sw+".ods", sheet_name=c_sw, engine="odf")
for a in Acc_Sw:
    dfs_out[a].to_excel(a+".ods", sheet_name=a, engine="odf")
    
for sw in All_Sw:
    #print(f"Currently in {sw=}")
    df = dfs_out[sw]
    rowsCnt, colsCnt = df.shape
    IFs = df.columns.values.tolist()
    f = open("CLI config."+sw+".txt", "w")
    #f.write("delete vlan.dat\n\n\nreload\nn\ny\n") # old: ("write erase\ny\n ...
    f.write("enable\nconfigure terminal\n")
    vlans = All_vlans_dict[sw]
    for vlan_num in vlans:
        f.write(f"vlan {vlan_num}\nexit\n")
    #assign VLANs to Interfaces
    for j in range(1, colsCnt):     #range(1, ... - to skip 1st col of VLAN ids
        #when in 0 row: command to enter the i-f. reset temp vars from last loop
        mode, col_Output, has_trunk = "", "", False
        for i in range(rowsCnt):
            if(df.iloc[i,j] == ""):
                continue
            #mode access
            if(df.iloc[i,j] == "A"):
                col_Output = "switchport mode access\nswitchport access vlan " + str(df.iloc[i,0])
                mode = "Access"
            if(df.iloc[i,j] == "Tagged"):
                mode = "Trunk"
                if(has_trunk):
                    text = "," + str(df.iloc[i,0])
                    col_Output += text
                    continue
                col_Output = "switchport mode trunk\nswitchport trunk allowed vlan " + str(df.iloc[i,0]) #may need to add col_Output = __"swithport trunk encapsulation dot1q\n"__ before "switchport mode ..."
                has_trunk = True
        if (has_trunk or mode):
            f.write(f"interface fastethernet {IFs[j]}\n")
            f.write(col_Output + "\nexit\n")
    f.write("exit\n")
    f.close()
print("OK!")