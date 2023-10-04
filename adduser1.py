#!/usr/bin/python
import os
import base64
import json
import subprocess
import sys


def main():
    status, serialnum = subprocess.getstatusoutput("dmidecode -s system-serial-number | grep -v SMB | grep -v dmide")
    if "VMware" in serialnum:
#       status, serialnum = commands.getstatusoutput("dmidecode -s system-uuid | grep -v SMB | grep -v dmide")
       status, serialnum = subprocess.getstatusoutput("dmidecode -s system-serial-number |sed s/VMware//g|sed s/-//g|sed s/\ //g")
       serialnum = serialnum[0:8] + '-' + serialnum[8:12] + '-' +  serialnum[12:16] + '-' +  serialnum[16:20] + '-' + serialnum[20:]
       value="vm"
    else:
       print(serialnum)
       value="physical"
    srno=serialnum.strip()
    status, output = subprocess.getstatusoutput("curl -s http://10.137.2.177/api/server/%s" % (srno))
    #status, output = commands.getstatusoutput("curl -s http://jiodc.ril.com/pei_internal/DBA/TOOL/PIM/TEST_IGF_PIMUser_json.php/REQ17-2775:SGH747W1CW" )

    output=output.strip()
    outputdata=json.loads(output)
    status, fcomm = subprocess.getstatusoutput("count=`cat /etc/group | grep tempsudo | wc -l`;if [ $count -ne \"1\" ] ;then groupadd -g 5052 tempsudo;echo '%tempsudo  ALL=(ALL)  NOPASSWD: ALL'>> /etc/sudoers;fi")
    outputj=outputdata["USER_LIST"]
    if value == "physical":
       data_ip=outputdata["DATA_IP"]
    elif value == "vm":
       data_ip=outputdata["VM_DATA_IP"]
       
    #outputj=output
    status, fjson = subprocess.getstatusoutput("echo %s | base64  --decode " % (outputj))
    #print fjson
    pdata=json.loads(fjson)
    return pdata,data_ip

def adduserf(pdata):
    l_count = len(pdata["users"])
    for count in range(l_count):
        username = pdata["users"][count]["username"]
        pimintegration = pdata["users"][count]["pimintegration"]
        description = pdata["users"][count]["description"]
        sudoers = pdata["users"][count]["sudoers"]
        gid = pdata["users"][count]["gid"]
        role = pdata["users"][count]["role"]
        Sgid = pdata["users"][count]["Sgid"]
        password = pdata["users"][count]["password"]
        expirydays = pdata["users"][count]["expirydays"]
        uid = pdata["users"][count]["uid"]
        #print username,pimintegration,description,sudoers,gid,role,Sgid,password,expirydays,uid
        if username == "root":
             print(("echo '%s' | passwd --stdin root;chage -M 99999 root" % (password)))
             ##:-
             status, fcomm = subprocess.getstatusoutput("echo '%s' | passwd --stdin %s" % (password,username))
             status, fcomm = subprocess.getstatusoutput("chage -M 99999 root")
        else:
             print(("groupadd -g %s %s" % (gid,username)))
             print(("useradd -u %s -g %s -c \"%s\"  %s" % (uid,gid,description,username)))
             #print ("echo '%s' | passwd --stdin %s" % (password,username))
             status, fcomm = subprocess.getstatusoutput("groupadd -g %s %s" % (gid,username))
             status, fcomm = subprocess.getstatusoutput("useradd -u %s -g %s -c \"%s\"  %s" % (uid,gid,description,username))
             status, fcomm = subprocess.getstatusoutput("echo '%s' | passwd --stdin %s" % (password,username))
             if username == "rjilsiem":
                 print(("chage -d 0  %s" % (username)))
                 print(("chage -M 180  %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("chage -d 0  %s" % (username))
                 status, fcomm = subprocess.getstatusoutput("chage -M 180  %s" % (username))
             elif username == "siatoolans":
                 print(("chage -E -1 -M -1  %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("chage -E -1 -M -1 %s" % (username))
             else:
                 print(("chage -M 99999 %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("chage -M 99999 %s" % (username))
             if username == "jioapp":
                 print(("usermod -G tempsudo %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("usermod -G tempsudo %s" % (username))
             if username == "oracle":
                 print(("usermod -G tempsudo %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("usermod -G tempsudo %s" % (username))
             if username == "pimadm":
                 print(("usermod -G 10 %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("usermod -G 10 %s" % (username))
             if username == "siatoolans":
                 print(("usermod -a -G wheel %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("usermod -a -G wheel %s" % (username))
             if username == "singoadm":
                 print(("usermod -a -G wheel %s" % (username)))
                 status, fcomm = subprocess.getstatusoutput("usermod -a -G wheel %s" % (username))
             if username == "jioiam":
                  status1, output = subprocess.getstatusoutput("cat /etc/sudoers | grep -i %s | wc -l" %(username))
                  if output == "0":
                      print(("echo '%s ALL=(ALL) NOPASSWD: /usr/bin/passwd, /usr/sbin/useradd, /usr/sbin/usermod, /usr/sbin/userdel, /usr/sbin/groupadd, /usr/sbin/groupdel, /usr/sbin/groupmod, /usr/bin/chage' >> /etc/sudoers " %(username)))
                      status, fcomm = subprocess.getstatusoutput("echo '%s ALL=(ALL) NOPASSWD: /usr/bin/passwd, /usr/sbin/useradd, /usr/sbin/usermod, /usr/sbin/userdel, /usr/sbin/groupadd, /usr/sbin/groupdel, /usr/sbin/groupmod, /usr/bin/chage' >> /etc/sudoers " %(username))
             elif username == "jiodbadm" or username == "jiodbsme":
                  status1, output = subprocess.getstatusoutput("cat /etc/sudoers | grep -i %s | wc -l" %(username))
                  if output == "0":
                      status, fcomm = subprocess.getstatusoutput("echo '%s ALL=(oracle) NOPASSWD: ALL' >> /etc/sudoers " %(username))
             elif username == "jmiam":
                  status1, output = subprocess.getstatusoutput("cat /etc/sudoers | grep -i %s | wc -l" %(username))
                  if output == "0":
                      status, fcomm = subprocess.getstatusoutput("echo '%s ALL=(ALL) NOPASSWD: /usr/bin/passwd, /usr/sbin/useradd, /usr/sbin/usermod, /usr/sbin/userdel, /usr/sbin/groupadd, /usr/sbin/groupdel, /usr/sbin/groupmod, /usr/bin/chage' >> /etc/sudoers " %(username))
             elif username == "jiobkpadm" or username == "jioappsup" or username == "jioapp":
                  status1, output = subprocess.getstatusoutput("cat /etc/sudoers | grep -i %s | wc -l" %(username))
             elif username == "jioadm":
                  status1, output = subprocess.getstatusoutput("cat /etc/sudoers | grep -i %s | wc -l" %(username))
                  if output == "0":
                      status, fcomm = subprocess.getstatusoutput("echo 'Cmnd_Alias JIOAMD_ACS= /usr/sbin/ufsdump, /usr/sbin/ufsrestore, /usr/sbin/fuser, /usr/bin/mt, /usr/sbin/iostat, /usr/sbin/devfsadm, /usr/bin/remsh, /usr/bin/touch, /usr/sbin/mknod,/usr/bin/mv,/usr/bin/cp,/usr/bin/tar,/usr/bin/cpio,/usr/bin/gzip,/usr/sbin/mount,/usr/sbin/umount,/usr/bin/ifconfig, /usr/sbin/ifup,/usr/bin/mkdir, /usr/bin/mkdir,/bin/mkdir,/usr/sbin/fsck, /usr/sbin/useradd, /usr/sbin/usermod,/usr/sbin/userdel, /usr/bin/cat, /usr/sbin/format, /usr/sbin/groupadd, /usr/sbin/groupdel, /usr/bin/du, /usr/sbin/route, /usr/bin/svcs, /usr/sbin/svcadm, /opt/SUNWexplo/bin/explorer,/usr/sbin/fbackup, /usr/sbin/frecover, /usr/sbin/vgcfgbackup, /usr/sbin/vgcfgrestore, /usr/sbin/vgchange, /usr/sbin/vgchgid, /usr/sbin/vgcreate, /usr/sbin/vgdisplay, /usr/sbin/vgexport, /usr/sbin/vgextend, /usr/sbin/vgimport, /usr/sbin/vgreduce, /usr/sbin/vgremove, /usr/sbin/vgscan, /usr/sbin/vgsync, /usr/sbin/lvchange, /usr/sbin/lvchange.run, /usr/sbin/lvcreate, /usr/sbin/lvdisplay, /usr/sbin/lvextend, /usr/sbin/lvlnboot, /usr/sbin/lvmchk, /usr/sbin/lvmerge, /usr/sbin/lvmmigrate, /usr/sbin/lvremove, /usr/sbin/lvrmboot, /usr/sbin/lvsplit, /usr/sbin/lvsync, /usr/sbin/lvreduce, /usr/sbin/fsadm, /usr/sbin/lvdisplay, /usr/sbin/lvextend, /usr/bin/passwd, /usr/sbin/mount, /opt/ignite/bin/make_tape_recovery, /opt/perf/bin/glance, /usr/sbin/ioscan, /usr/sbin/insf, /usr/sbin/pvchange, /usr/sbin/pvck,  /usr/sbin/pvcreate, /usr/sbin/pvdisplay, /usr/sbin/pvmove, /usr/sbin/pvremove, /usr/lbin/getprpw, /usr/lbin/modprpw, /usr/sbin/kmtune, /usr/bin/cpio, /usr/sbin/backup, /usr/sbin/restore,/usr/sbin/lsuser, /usr/bin/chuser, /usr/bin/logins, /usr/bin/mkgroup, /usr/sbin/chfs, /usr/sbin/umount, /usr/sbin/varyonvg, /usr/sbin/varyoffvg, /usr/bin/chgrp, /etc/route,  /usr/bin/startsrc, /usr/bin/stopsrc, /usr/bin/refresh, /usr/sbin/chdev, /usr/sbin/vmo -a, /usr/sbin/ioo -a , /usr/sbin/aioo -a, /usr/sbin/snap, /usr/openv/netbackup/bin/bplist, /usr/sbin/swlist, /usr/bin/ipcs, /usr/contrib/bin/show_patches, /opt/ignite/bin/print_manifest, /usr/bin/model, /usr/sbin/lanscan, /usr/sbin/exportfs, /usr/sbin/swapinfo, /usr/sbin/parstatus, /usr/bin/strings, /usr/bin/pwdadm, sudoedit /etc/hosts, /usr/bin/tail, /usr/sbin/dmidecode, /usr/bin/chage, /usr/bin/getconf, /usr/sbin/vparstatus, /usr/sbin/parstatus, /opt/ignite/bin/make_net_recovery, /usr/sbin/cmviewcl,/usr/sbin/dmesg, /usr/sbin/ufsdump, /usr/sbin/restore, /usr/bin/ls, /usr/bin/unlock,/usr/sbin/pam_tally2,/sbin/pam_tally2, /usr/bin/faillog,/bin/faillog,/opt/VRTSvcs/bin/haconf,/opt/VRTSvcs/bin/hastatus,/opt/VRTSvcs/bin/hares,/opt/VRTSvcs/bin/hagrp,/sbin/lltstat,/sbin/lltconfig,/sbin/gabconfig,/opt/VRTSvcs/bin/vxfenadm,/opt/VRTS/bin/vxdg,/opt/VRTS/bin/vxassist,/opt/VRTS/bin/vxresize,/opt/VRTS/bin/vxprint, /opt/VRTS/bin/vxvol,/sbin/vxdmpadm,/opt/VRTS/bin/vxlist,/Opt/VRTS/bin/vxdisksetup,/Opt/VRTS/bin/vxdiskunsetup,/opt/VRTS/bin/vxdiskadm,/opt/VRTS/bin/mkfs,/opt/VRTS/bin/mount,/opt/VRTS/bin/umount,/opt/VRTS/bin/vxdctl,/opt/VRTS/bin/vxevac,/opt/VRTS/bin//vxedit,/opt/VRTS/bin/vxumount, /opt/VRTS/bin/fsadm,/opt/VRTS/bin/fstyp,/opt/VRTS/bin/ddladm, /sbin/dump, /sbin/restore, /sbin/fuser, /usr/bin/iostat, /bin/touch, /bin/mknod, /bin/mv, /bin/cp, /bin/tar, /bin/cpio, /usr/bin/gzip, /bin/mount, /bin/umount, /sbin/ifconfig, /sbin/ifup, /sbin/ifdown, /bin/mkdir, /sbin/e2fsck, /bin/mkdir, /sbin/fsck, /usr/sbin/useradd, /usr/sbin/usermod, /usr/sbin/userdel, /bin/cat, /sbin/fdisk, /usr/sbin/groupadd, /usr/sbin/groupdel, /usr/bin/du, /sbin/route, /sbin/service, /sbin/chkconfig, /usr/sbin/sosreport, /sbin/dumpe2fs, /sbin/vgcfgbackup, /sbin/vgcfgrestore, /sbin/vgchange, /sbin/vgs, /sbin/vgcreate, /sbin/vgdisplay, /sbin/vgexport, /sbin/vgextend, /sbin/vgimport, /sbin/vgreduce, /sbin/vgremove, /sbin/vgscan, /sbin/lvchange, /sbin/lvscan, /sbin/lvcreate, /sbin/lvdisplay, /sbin/lvextend, /sbin/lvs, /sbin/lvmdiskscan, /sbin/lvremove, /sbin/lvreduce, /sbin/fsadm, /sbin/lvrename, /sbin/lvresize, /usr/bin/passwd, /bin/mount, /sbin/pvscan, /sbin/pvs, /sbin/pvchange, /sbin/pvresize, /sbin/pvcreate, /sbin/pvdisplay, /sbin/pvmove, /sbin/pvremove, /sbin/sysctl, /usr/openv/netbackup/bin/admincmd/bpcoverage, /usr/openv/netbackup/bin/bpclntcmd, /usr/openv/netbackup/bin/admincmd/bptestbpcd, /usr/openv/netbackup/bin/admincmd/bpps, /usr/openv/netbackup/bin/bplist, /usr/openv/volmgr/bin/vmquery, /usr/openv/netbackup/bin/admincmd/bpplclients, /usr/openv/netbackup/bin/admincmd/bppllist, /usr/openv/netbackup/bin/admincmd/bpdbjobs' >> /etc/sudoers ")
                      status, fcomm = subprocess.getstatusoutput("echo '%s ALL=(ALL) NOPASSWD: JIOAMD_ACS' >> /etc/sudoers" %(username))
             elif username == "siatoolans":
                  status1, output = subprocess.getstatusoutput("cat /etc/sudoers | grep -i %s | wc -l" %(username))
                  if output == "0":
                      print(("echo '%s ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers" %(username)))
                      status, fcomm = subprocess.getstatusoutput("echo '%s ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers" %(username))
                      print(("echo 'Defaults:%s            !requiretty' >> /etc/sudoers" %(username)))
                      status, fcomm = subprocess.getstatusoutput("echo 'Defaults:%s            !requiretty' >> /etc/sudoers" %(username))
              status, fcomm = commands.getstatusoutput("mkdir -p /home/siatoolans/.ssh")                      
                      status, fcomm = subprocess.getstatusoutput("echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC74NLjm6S3z+/fixy0lecCdCqh7rTD0LwTsegBKwKoUB7w1szDZLWEdfgh8b+FFmV7rXtpXNM4nJYdKP37oiQOGxy+c4I744MYTL1I8hyPGGAzhwRYuUGGVvSH6DX3N98lIhunXbmUlNyj9puqiGGiLzQgQP1f2TOqsrFbaEq5HqPuypa7XIAeiZIbsNjjZXbG1hpEX0OMfEIXpppMxxU5bcv067o7co7hSMk5nthmBweORpLhZ3wr3w+hM37hezndt4joJ2TewdCvMkuSJSp4M3IIy/fYPuQsn9ExB4J3u8VOHAM9r0NGPfpE9YbwMl1G5Vpnyw0zv4wQe/g9FNUj siatoolans@NVMBD2BPH250V02' > /home/siatoolans/.ssh/authorized_keys")
		      status, fcomm = subprocess.getstatusoutput("echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXRxvX80AxtyFG5bK6LdWY8aq5lf3vQA4benXciQ81T96ZeU8xBPcXHAXoToOrTVSWG3REX7qb1IbLKaBxj19A9gEWtMb2jdjFZ24pGoq7joKbSImwgvnQIinHCySiHVTMFkGibWMMFuQUEJIs3z6SNUFLgFKfFV8rs16Gjn8b/yQlX/vEzj69Utf3NYBcZATxrvVlkFy7cHtIT0M+VBbhhld/A6+gy7dBPYcBMj0rs0a4KeH8eZ1dfUJ04O+cRntKFOpV+AkdbPO+SRY5/D4o7gsL201MtxNUpiIbRlPr1wcwuvZM1H0kvwx96ZkEr4uoxjhedggAZhYGyRI75DPr siatoolans@NVMBD2BPH250V03' >> /home/siatoolans/.ssh/authorized_keys")
    		      status, fcomm = subprocess.getstatusoutput("echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDb1Yrh3uLVV9VVMo0EvMNFaumoF48tgoeyr0WAS0H2Xe6LHlxsYYmcZ096PhywBE+6QJ/wHhZmDuU/AVWwRqDS3EEUyicqWjiEgyt2EuYvJ1h4HKzD6uLc+3+sjpo3fjFE6aaL+52HKfpcZVXx1YBVmUkIrdMKTZJHJ5Wq9e18e4yt/3M+kLIVvHMFF0r3MPmrR+FYI3lG9YUaS+B8qyUc78iGXmU4Oo9kJclWo1YtGD+V3MfHSoYwSA8JGdxw3Rsa2Xs6hGY5AJ9ufV0UXWY4hZu/u8Syk0U57nWYkvL+i2wFxgkcO9ERojxMWa3aStQsvPlq67IBaLoJ83UVhCqB siatoolans@NVMBD2BPI230V02' >> /home/siatoolans/.ssh/authorized_keys")
		      status, fcomm = subprocess.getstatusoutput("echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDxJXCSoE8w0mr4uJVIzrj9NzrkaKXwNQIoImx9D4qQ61MuJ8R5FmWWcdUoqFrjV8ksS3v5z4boBppUZhEYp9EbVdiRsdI9aPyCH5IDfoKujig2ynE4hYKzVOPSZauF509i6RlI2eVxB514Aj1rwVDp3VZQ+kLQ0+rQ2ZkQAOfm28ipsZmMe3IfGEYI5QrhgvkIZPsXZZYgx2lzZEvqVzYr+BUbNINxpdqfdSU+21v1tOvis3zVuE5tdTqeLp/QxVisDXtVALQ0sscW00vSYPhOpVosz3SkF9oFVs/xWUirlHiuPYVXMWUJmNV5SUCopT0W/Gw3IH9umFev89L0cVQt siatoolans@NVMBD2BPI230V03' >> /home/siatoolans/.ssh/authorized_keys")
		      status, fcomm = subprocess.getstatusoutput("chown -R siatoolans:siatoolans /home/siatoolans;chmod -R 700 /home/siatoolans/.ssh;chmod 600 /home/siatoolans/.ssh/authorized_keys")

             else:
                  status1, output = subprocess.getstatusoutput("cat /etc/sudoers | grep -i %s | wc -l" %(username))
                  if output == "0":
                      print(("echo '%s ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers" %(username)))
                      status, fcomm = subprocess.getstatusoutput("echo '%s ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers" %(username))

def checkpim(pdata,dataip):
    l_count = len(pdata["users"])
    pimenvvar=pdata["pimenv"]
    data = ("{\"dataip\":\"%s\",\"os\":\"LINUX\",\"pimenv\":\"%s\"}" %(dataip,pimenvvar))
    status, fcomm = subprocess.getstatusoutput("curl  -d \'%s\' http://10.137.2.177/pimverifyapi/verifypim -X POST -H \"Content-Type: application/json\"" %(data))
    print(data)
    print(status)

def addpimadm(pdata,dataip):
    l_count = len(pdata["users"])
    pimenvvar=pdata["pimenv"]
    for count in range(l_count):
        username = pdata["users"][count]["username"]
        pimintegration = pdata["users"][count]["pimintegration"]
        pimsafename = pdata["users"][count]["pimsafename"]
        #pimsafename =  "API"
        #platformid = "UnixSSH"
        platformid = pdata["users"][count]["platformid"]
        description = pdata["users"][count]["description"]
        sudoers = pdata["users"][count]["sudoers"]
        gid = pdata["users"][count]["gid"]
        role = pdata["users"][count]["role"]
        Sgid = pdata["users"][count]["Sgid"]
        password = pdata["users"][count]["password"]
        expirydays = pdata["users"][count]["expirydays"]
        uid = pdata["users"][count]["uid"]
        data = ("{\"dataip\":\"%s\",\"os\":\"LINUX\",\"pimenv\":\"%s\"}" %(dataip,pimenvvar))
        #status, fcomm = commands.getstatusoutput("curl  -d %s http://10.137.2.117:5012/addToPIM -X POST -H \"Content-Type: application/json\"" %(data))
        #print username,pimintegration,description,sudoers,gid,role,Sgid,password,expirydays,uid
        if username == "pimadm":
             accountName = platformid + "-" + dataip +"-"
             accountNamef = accountName + username
             data = ("{\"account\": {\"username\": \"%s\", \"platformID\": \"%s\", \"safe\": \"%s\", \"disableAutoMgmt\": \"false\", \"accountName\": \"%s\", \"address\": \"%s\",\"password\": \"%s\"},\"pimenv\":\"%s\"}" %(username,platformid,pimsafename,accountNamef,dataip,password,pimenvvar))
             print(("curl  -d \'%s\' http://10.137.2.177/pimapi/addToPIM -X POST -H \"Content-Type: application/json\"" %(data)))
             status, fcomm = subprocess.getstatusoutput("curl  -d \'%s\' http://10.137.2.177/pimapi/addToPIM -X POST -H \"Content-Type: application/json\"" %(data))
             print(status)
             return accountName,pimsafename

def addpimf(pdata,accountName,pimadmsafe,dataip):
    l_count = len(pdata["users"])
    pimenvvar=pdata["pimenv"]
    #dataip="10.144.100.112"
    for count in range(l_count):
        username = pdata["users"][count]["username"]
        pimintegration = pdata["users"][count]["pimintegration"]
        pimsafename = pdata["users"][count]["pimsafename"]
        #pimsafename = "API"
        platformid = pdata["users"][count]["platformid"]
        #platformid = "UnixSSH"
        description = pdata["users"][count]["description"]
        sudoers = pdata["users"][count]["sudoers"]
        gid = pdata["users"][count]["gid"]
        role = pdata["users"][count]["role"]
        Sgid = pdata["users"][count]["Sgid"]
        password = pdata["users"][count]["password"]
        expirydays = pdata["users"][count]["expirydays"]
        uid = pdata["users"][count]["uid"]
        data = ("{\"dataip\":\"%s\",\"os\":\"LINUX\",\"pimenv\":\"%s\"}" %(dataip,pimenvvar))
        #status, fcomm = commands.getstatusoutput("curl  -d %s http://10.137.2.117:5012/addToPIM -X POST -H \"Content-Type: application/json\"" %(data))
        #print username,pimintegration,description,sudoers,gid,role,Sgid,password,expirydays,uid
        if username != "pimadm" and pimintegration.lower() == "yes":
             accountNamef = accountName + username
             accountNamep = accountName + "pimadm"
             data = ("{\"pimenv\":\"%s\",\"account\": { \"username\": \"%s\", \"platformID\": \"%s\", \"safe\": \"%s\", \"disableAutoMgmt\": \"false\", \"accountName\": \"%s\", \"address\": \"%s\",\"password\": \"%s\", \"properties\": [ {\"Key\":\"ExtraPass3Name\", \"Value\": \"%s\"},{\"Key\":\"ExtraPass3Folder\", \"Value\":\"root\"},{\"Key\":\"ExtraPass3Safe\", \"Value\":\"%s\"}]}}" %(pimenvvar,username,platformid,pimsafename,accountNamef,dataip,password,accountNamep,pimadmsafe))
             print(data)
             #print ("curl  -d \'%s\' http://10.137.2.117:5012/addToPIM -X POST -H \"Content-Type: application/json\"" %(data))
             status, fcomm = subprocess.getstatusoutput("curl  -d \'%s\' http://10.137.2.177/pimapi/addToPIM -X POST -H \"Content-Type: application/json\"" %(data))
             print(status)

if __name__ == "__main__":
    adduser = sys.argv[1]
    addpim = sys.argv[2]
    if (adduser and addpim):
        adduservar=adduser.lower()
        addpimvar=addpim.lower()
        print(adduservar)
        if adduservar == "y" and addpimvar == "y":
            pdata,dataip=main()
            adduserf(pdata)           
            checkpim(pdata,dataip)
            accountName,pimadmsafe=addpimadm(pdata,dataip)
            addpimf(pdata,accountName,pimadmsafe,dataip)
        elif adduservar == "y":
           adduservar=adduser.lower()
           print(adduservar)
           if adduservar == "y":
            pdata,dataip=main()
            adduserf(pdata)           
        elif addpimvar == "y":
           addpimvar=addpim.lower()
           if addpimvar == "y":
            pdata,dataip=main()
            checkpim(pdata,dataip)
            accountName,pimadmsafe=addpimadm(pdata,dataip)
            addpimf(pdata,accountName,pimadmsafe,dataip) 
