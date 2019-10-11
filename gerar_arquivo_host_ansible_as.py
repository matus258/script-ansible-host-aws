#!/usr/bin/python

import os
import boto3
import json
import re
import time
import paramiko
import sys
import getopt

checked = []
host_ip=[]
pem = ''
apath =''
keypath=''
name =''
akid=''
secret=''
all_hosts = False
pm = 0
no_host =[]
exist_host=False
try:
    opts, args = getopt.getopt(sys.argv[1:],"hp:k:ti:a:s:",["anspath=","keypath=","all=","ip=","akid=","secret="])
except Exception as e:
    print(e)
    sys.exit(1)
for opt, arg in opts:
    if opt == '-h':
        print('para todos os hosts: \n test.py -p "/caminho/para/playbook" -k "/caminho/para/pem" -a "akid" -s "aksecret" -t \n para hosts especificos: \n test.py -p "/caminho/para/playbook" -k "/caminho/para/pem" -a "akid" -s "aksecret" -i "host-ip1,host-ip2"')
        sys.exit()
    elif opt in ('-p', '--anspath'):
        apath = arg
        pm += 1
    elif opt in ('-k','--keypath'):
        keypath = arg
        pm += 1
    elif opt in ('-t','--all'):
        all_hosts = True
        pm += 1
    elif opt in ('-i','--ip'):
        pm += 1
        if not all_hosts:
            arg = arg.split(',')
            host_ip = arg
    elif opt in ('-a','--akid'):
        akid = arg
        pm += 1
    elif opt in ('-s','--secret'):
        secret = arg
        pm += 1
if pm != 5:
    print('para todos os hosts: \n test.py -p "/caminho/para/playbook" -k "/caminho/para/pem" -a "akid" -s "aksecret" -t \n para hosts especificos: \n test.py -p "/caminho/para/playbook" -k "/caminho/para/pem" -a "akid" -s "aksecret" -i "host-ip1,host-ip2"')
    sys.exit(1)

with open(apath+'hosts', 'w') as f:
	w = f.write("")
ec2 = boto3.client('ec2', region_name='us-east-1', aws_access_key_id=akid,
    aws_secret_access_key=secret)
response = ec2.describe_instances()

if all_hosts:
    for res in response['Reservations']:
        for ins in res['Instances']:
            if ins['State'].get('Name') == 'running':
                i = 0
                keyname=ins.get('KeyName','')
                for net in ins['NetworkInterfaces']:
                    if net.get('PrivateIpAddress'):
                        host_ip = net.get('PrivateIpAddress')
                        if ins.get('Tags'):
                            for tag in ins['Tags']:
                                if tag['Key'] == 'Name':
                                    name = tag['Value']
                print("Host: "+name+" ip: "+host_ip)                    
                pem = keypath+keyname+'.pem'
                if not host_ip in checked:
                    try:
                        k = paramiko.RSAKey.from_private_key_file(pem)
                        username_host=['ubuntu','centos','ec2-user','admin','root']
                        con = False
                        while not con:
                            username_host[i]
                            try:
                                ssh = paramiko.SSHClient()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.connect(host_ip, username=username_host[i], pkey=k,timeout=15)
                                print("Conectado com usuario: "+username_host[i] +"\n")
                                if username_host[i] == 'ubuntu':
                                    with open(apath+'hosts', 'a') as f:
                                        w = f.write(host_ip+' ansible_ssh_private_key_file='+pem+' ansible_user='+username_host[i]+' ansible_python_interpreter=/usr/bin/python3'+' zabbix_hostname=\"'+name+'-'+host_ip+'\"\n')
                                else:
                                    with open(apath+'hosts', 'a') as f:
                                        w = f.write(host_ip+' ansible_ssh_private_key_file='+pem+' ansible_user='+username_host[i]+' zabbix_hostname=\"'+name+'-'+host_ip+'\"\n')
                                con = True
                            except Exception as e:
                                con = False
                                i +=1
                                if i ==5:
                                    print(name +' user nao encontrado')
                                    break
                    except Exception as e:
                        print(str(e)+"\n")
                    checked.append(host_ip)
else:
    for res in response['Reservations']:
        for ins in res['Instances']:
            i = 0
            keyname=ins.get('KeyName','')
            for net in ins['NetworkInterfaces']:
                if net.get('PrivateIpAddress'): 
                    ip = net.get('PrivateIpAddress')
                    for par_ip in host_ip:
                        if ip == par_ip:
                            if ins.get('Tags'):
                                for tag in ins['Tags']:
                                    if tag['Key'] == 'Name':
                                        name = tag['Value']
                            print("Host: "+name+" ip: "+par_ip) 
                            pem = keypath+keyname+'.pem'
                            try:
                                k = paramiko.RSAKey.from_private_key_file(pem)
                                username_host=['ubuntu','centos','ec2-user','admin','root']
                                con = False
                                while not con:
                                    username_host[i]
                                    try:
                                        ssh = paramiko.SSHClient()
                                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                        ssh.connect(par_ip, username=username_host[i], pkey=k,timeout=15)
                                        print("Conectado com usuario: "+username_host[i] +"\n")
                                        if username_host[i] == 'ubuntu':
                                            with open(apath+'hosts', 'a') as f:
                                                w = f.write(par_ip+' ansible_ssh_private_key_file='+pem+' ansible_user='+username_host[i]+' ansible_python_interpreter=/usr/bin/python3'+' zabbix_hostname=\"'+name+'-'+par_ip+'\"\n')
                                        else:
                                            with open(apath+'hosts', 'a') as f:
                                                w = f.write(par_ip+' ansible_ssh_private_key_file='+pem+' ansible_user='+username_host[i]+' zabbix_hostname=\"'+name+'-'+par_ip+'\"\n')
                                        con = True
                                    except Exception as e:
                                        con = False
                                        i +=1
                                        if i ==5:
                                            print(e)
                                            print(name +' user nao encontrado')
                                            break
                            except Exception as e:
                                print(str(e)+"\n")



