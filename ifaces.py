import re
import subprocess

def enum_if():
    ic = subprocess.check_output(["ifconfig"]).splitlines()
    ifs = {}
    if_name = '?'

    for line in ic:
        i = re.match('\A\w+', line)
        if i is not None:
            if_name = i.group(0)
        else:
            ip = re.search(' inet addr:(\d+.\d+.\d+.\d+) ', line)
            if ip is not None:
                ifs.update({if_name : ip.group(1)})
    print "Interfaces: "
    print ifs
    return ifs


def choose_ip():
    ifs = enum_if()
    wlan0 = ifs.get('wlan0')
    if wlan0 is not None:
        return wlan0
    for name in ifs:
        if name[0] == 'w':
            return ifs.get(name)
    eth0 = ifs.get('eth0')
    if eth0 is not None:
        return eth0
    for name in ifs:
        if name != 'lo':
            return ifs.get(name)
    return ifs.get('lo')
