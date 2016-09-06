#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import redis
import sys
import datetime
import traceback
from sendmail import send_mail


to_list = ['xiu8idc@xiu8.com','xiaowen@xiu8.com'] 
mail_host = "mail.xiu8.com"  #设置服务器
mail_user = "xiu8idc@xiu8.com"    #用户名
mail_pass = "FGJAxJdLQg"   #口令 
mail_postfix = "xiu8.com"  #发件箱的后缀
mail_addresser = "redis_xiu8idc"
log = '/root/redis_db_bak.py/redis_bak.log'
#mail_sub = "redis_bak"
#mail_content = "redis_neirong"

def read_iplist_conf(ip_filename):
    filename = open(ip_filename,'r')
    ip_dict = {}
    for i in filename.readlines():
        master_ip,backup_ip,port,redis_passwd = i.strip().split(',')
        ip_dict[master_ip] = backup_ip,port,redis_passwd
    filename.close()
    return ip_dict

def redis_save(redis_ip):
    for i in redis_ip.keys():
        master_ip = i
        bak_ip,redis_port,redis_passwd = redis_ip[i]
        try: 
            redis_bakup = redis.Redis(host=master_ip, port=int(redis_port), password=redis_passwd)
            chk_key = redis_bakup.get('redis_saof_bak')
            if chk_key == 'yes':
                print "bak_start"            
            else:
                print "fasongyoujian" 
        except Exception,error: 
            f=open(log,'a')  
            failed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") 
            f.write("----------------------------------------------------------------------------\n")
            f.write(failed_time)
            f.write("\n")
            traceback.print_exc(file=f)  
            f.write("----------------------------------------------------------------------------\n")
            f.flush()  
            f.close()  
            send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,'reids_bak_connect_failed','Redis connection fails, please view the log')



if __name__ == "__main__":
    ipdict = read_iplist_conf('ip_list.conf')
    redis_save(ipdict)
    
