#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import redis
import sys
import datetime
import traceback
import paramiko
from sendmail import send_mail


reload(sys)
sys.setdefaultencoding( "utf-8" )


to_list = ['xiu8idc@xiu8.com','xiaowen@xiu8.com'] 
mail_host = "mail.xiu8.com"  #设置服务器
mail_user = "xiu8idc@xiu8.com"    #用户名
mail_pass = "FGJAxJdLQg"   #口令 
mail_postfix = "xiu8.com"  #发件箱的后缀
mail_addresser = "redis_xiu8idc"
log = '/root/redis_db_bak/redis_bak_error.log'
access_log = '/root/redis_db_bak/redis_bak_access.log'
dump_filename = '/root/redis_db_bak/dump_filename'
appendonly_filename = '/root/redis_db_bak/appendonly_filename'

def read_iplist_conf(ip_filename):
    filename = open(ip_filename,'r')
    ip_dict = {}
    for i in filename.readlines():
        master_ip,backup_ip,port,redis_passwd = i.strip().split(',')
        ip_dict[master_ip] = backup_ip,port,redis_passwd
    filename.close()
    return ip_dict

def ssh_commnd(ip,port,username,passwd):
    save_time = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S-%f")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port,username,passwd)

    dump_dst = '/home/xiuba/redis_db_bak/dump.rdb_' + save_time
    appendonly_dst = '/home/xiuba/redis_db_bak/appendonly.aof_' + save_time

    dump_save = 'cp /var/lib/redis/dump.rdb ' + dump_dst 
    appendonly_save = 'cp /var/lib/redis/appendonly.aof ' + appendonly_dst

    stdin, stdout, stderr = ssh.exec_command(dump_save)
    dump_status = 'succeed'
    for i in stderr.readlines():
        dump_status = i
    if dump_status == 'succeed':
        dump_file = open(dump_filename,'r')
        dump_save_name = dump_file.readlines()[0].strip()
        dump_file.close()
        dump_file = open(dump_filename,'w')
        dump_file.write(dump_dst) 
        dump_file.write("\n") 
        dump_file.close()
        cmd = 'rm -f ' + dump_save_name
        cmd_status = 'succeed'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        for i in stderr.readlines():
            cmd_status = i
        if cmd_status != 'succeed':
            send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_db_nodel','Redis backup file delete failed, please view the log')
            log_write(log,cmd_result_status)
        else:
            log_write(access_log,'dump.rdb file backup success')
    else:
        log_write(log,dump_status)

    stdin, stdout, stderr = ssh.exec_command(appendonly_save)
    appendonly_status = 'succeed'
    for i in stderr.readlines():
       appendonly_status = i

    if appendonly_status == 'succeed':
        appendonly_file = open(appendonly_filename,'r')
        appendonly_save_name = appendonly_file.readlines()[0].strip()
        appendonly_file.close()
        appendonly_file = open(appendonly_filename,'w')
        appendonly_file.write(appendonly_dst)
        appendonly_file.write("\n")
        appendonly_file.close()
        cmd = 'rm -f ' + appendonly_save_name
        appcmd_status = 'succeed'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        for i in stderr.readlines():
            appcmd_status = i
        if appcmd_status != 'succeed':
            send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_db_nodel','Redis backup file delete failed, please view the log')
            log_write(log,cmd_result_status)
        else:
            log_write(access_log,'appendonly.aof file backup success')
    else:
        log_write(log,appendonly_status)

    ssh.close()

    result_list = []
    result_list.append(dump_status)
    result_list.append(appendonly_status)

    return result_list

def redis_connect(redis_ip):
    for i in redis_ip.keys():
        master_ip = i
        bak_ip,redis_port,redis_passwd = redis_ip[i]
        try: 
            redis_bakup = redis.Redis(host=master_ip, port=int(redis_port), password=redis_passwd)
            chk_key = redis_bakup.get('redis_saof_bak')
            if chk_key == 'yes':
                dump_result,appendonly_result = ssh_commnd(bak_ip,22,'root','xiuba123')
                log_write(access_log,'Redis connection is successful')
                if dump_result != 'succeed'  or appendonly_result != 'succeed':
                    send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_bak_failed','Redis persistence backup error, please see the log') 
            else:
                f=open(log,'a')
                failed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                f.write(failed_time)
                f.write("\n")
                f.write(master_ip)
                f.write(" The key error\n")
                f.write("----------------------------------------------------------------------------\n")
                f.flush()
                f.close()
                send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_bak_key_failed','Redis keys error, please see the log') 
        except Exception,error: 
            f=open(log,'a')  
            failed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") 
            f.write(failed_time)
            f.write("\n")
            f.write(master_ip)
            f.write(" ")
            traceback.print_exc(file=f)  
            f.write("----------------------------------------------------------------------------\n")
            f.flush()  
            f.close()  
            send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_bak_connect_failed','Redis connection fails, please view the log')

def log_write(log_file,conment,ip="None_ip"):
    f=open(log_file,'a')
    failed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    f.write(failed_time)
    f.write("\n")
    f.write(conment)
    f.write("\n")
    f.write("----------------------------------------------------------------------------\n")
    f.flush()
    f.close()

if __name__ == "__main__":
    ip_filename = '/root/redis_db_bak/ip_list.conf'
    f = open('redis_bak_access.log','a')
    ipdict = read_iplist_conf(ip_filename)
    redis_connect(ipdict)
    
