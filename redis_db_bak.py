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


to_list = ['test@test.com','test@test.com'] 
mail_host = "mail.test.com"  #设置服务器
mail_user = "test@test.com"    #用户名
mail_pass = "test"   #口令 
mail_postfix = "test.com"  #发件箱的后缀
mail_addresser = "test"
log = '/root/redis_db_bak/redis_bak_error.log'
access_log = '/root/redis_db_bak/redis_bak_access.log'
dump_filename = '/root/redis_db_bak/dump_filename'
appendonly_filename = '/root/redis_db_bak/appendonly_filename'
local_ip = '192.168.1.201'

def read_iplist_conf(ip_filename):
    filename = open(ip_filename,'r')
    ip_dict = {}
    for i in filename.readlines():
        redis_name,master_ip,backup_ip,port,redis_passwd,redis_src,redis_dst = i.strip().split(',')
        ip_dict[redis_name] = master_ip,backup_ip,port,redis_passwd,redis_src,redis_dst
    filename.close()
    return ip_dict

def ssh_commnd(ip,port,username,passwd,redisbak_src,redisbak_dst,redis_port):
    save_time = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S-%f")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port,username,passwd)

    dump_dst = redisbak_dst + '/dump.rdb_' + ip + '_' + str(redis_port) + '_' + save_time
    appendonly_dst = redisbak_dst + '/appendonly.aof_' + ip + '_' + str(redis_port) + '_' + save_time

    dump_save = 'cp ' + redisbak_src + '/dump.rdb ' + dump_dst 
    appendonly_save = 'cp ' + redisbak_src + '/appendonly.aof ' + appendonly_dst

    stdin, stdout, stderr = ssh.exec_command(dump_save)
    dump_status = 'succeed'

    for i in stderr.readlines():
        dump_status = i

    if dump_status == 'succeed':
        success_conment = ip + '_' + redis_port + ' Redis dump.db persistent file backup successfully'
        log_write(access_log,ip,success_conment) 
    else:
        faild_conment = ip + '_' + redis_port + local_ip +' Redis dump.db persistence failed to backup file'
        log_write(log,dump_status,faild_conment)
        send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reid_dump_bak_fiaid',faild_conment)
        

    stdin, stdout, stderr = ssh.exec_command(appendonly_save)
    appendonly_status = 'succeed'
    for i in stderr.readlines():
       appendonly_status = i

    if appendonly_status == 'succeed':
        success_conment = ip + '_' + redis_port + ' Redis appendonly.aof persistent file backup successfully'
        log_write(access_log,ip,success_conment) 
    else:
        faild_conment = ip + '_' + redis_port + local_ip + ' Redis appendonly.aof persistence failed to backup file'
        log_write(log,appendonly_status,conment)
        send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'Redis_appendonly_bak_fiaid',faild_conment)

    ssh.close()

    result_list = []
    result_list.append(dump_status)
    result_list.append(appendonly_status)

    return result_list

def redis_connect(redis_ip):
    for i in redis_ip.keys():
        redis_name = i
        master_ip,bak_ip,redis_port,redis_passwd,redisbak_src,redisbak_dst = redis_ip[i]
        try: 
            redis_bakup = redis.Redis(host=master_ip, port=int(redis_port), password=redis_passwd)
            log_write(access_log,'Redis connection is successful')
            chk_key = redis_bakup.get('redis_saof_bak')
            if chk_key == 'yes':
                dump_result,appendonly_result = ssh_commnd(bak_ip,22,'root','test',redisbak_src,redisbak_dst,redis_port)
                if dump_result != 'succeed'  or appendonly_result != 'succeed':
                    send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_bak_failed','192.168.1.201 Redis persistence backup error, please see the log') 
            else:
                conment = master_ip + '_' + redis_port + " The key error"
                log_write(log,master_ip,conment)
                send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_bak_key_failed','192.168.1.201 Redis keys error, please see the log') 
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

def log_write(log_file,conment,conment_2=''):
    f=open(log_file,'a')
    failed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    f.write(failed_time)
    f.write("\n")
    f.write(conment)
    f.write("\n")
    f.write(conment_2)
    f.write("\n")
    f.write("----------------------------------------------------------------------------\n")
    f.flush()
    f.close()

def procedure_execute():
    shijian = datetime.datetime.now().strftime("%H%M")  
    if shijian > 1000 and shijian < 1200:
        send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,mailto_list,'Redis backup','Redis backup procedures have been executed') 

if __name__ == "__main__":
    ip_filename = '/root/redis_db_bak/ip_list.conf'
    ipdict = read_iplist_conf(ip_filename)
    redis_connect(ipdict)
    procedure_execute()
    
