#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import smtplib  
from email.mime.text import MIMEText  
mailto_list = ['xiu8idc@xiu8.com','xiaowen@xiu8.com'] 
mail_host = "mail.xiu8.com"  #设置服务器
mail_user = "xiu8idc@xiu8.com"    #用户名
mail_pass = "FGJAxJdLQg"   #口令 
mail_postfix = "xiu8.com"  #发件箱的后缀
mail_addresser = "xiu8idc"
mail_sub = "zhuti"
mail_content = "neirong"


  
def send_mail(mail_host,mail_user,mail_pass,mail_postfix,mail_addresser,to_list,sub,content):  
    me=mail_addresser+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content,_subtype='plain',_charset='gb2312')  
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        server = smtplib.SMTP()  
        server.connect(mail_host)  
        server.login(mail_user,mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception, e:  
        print str(e)  
        return False  
if __name__ == '__main__':  
   send_mail(host,user,passwd,pastfix,addresser,list,sub,content)
