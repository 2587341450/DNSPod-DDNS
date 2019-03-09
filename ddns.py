import re
import requests
import json

pat = r"[0-9]+(?:\.[0-9]+){0,3}"    #正则匹配ip地址
domain = "your doamin" #域名
sub_domain = "@"        #主机记录
domain_type = "A"       #记录类型
token = "id,key"    #DNSPod token
log_file_path = "/log/ddns.log"                     #日志文件路径
def get_local_ip():
    '''
    @description: 获取本机的公网ip地址
    @return: ip地址,字符型
    '''
    global pat
    ip_url = "http://myip.ipip.net/"
    res = requests.get(url=ip_url ,timeout = 8)
    return re.search(pat,res.text).group()
def get_domain_ip():
    '''
    @description: 获取域名当前的记录值ip
    @return: (record_id,ip) 元组型
    '''
    ip_url = "https://dnsapi.cn/Record.List"
    my_data = {"login_token":token,\
                "format":"json",\
                    "domain":domain ,\
                        "sub_domain":sub_domain ,\
                            "record_type": domain_type,\
                                "offset":"0",\
                                    "length":"3"}
    # print(my_data)
    res = requests.post(url=ip_url ,data=my_data ,timeout=5)
    record_data = json.loads(res.text)['records'][0]
    return (record_data['id'],record_data['value'])

def modify_domain_ip(new_ip ,record_id):
    '''
    @description: 修改域名记录值
    @param new_ip为字符型ip地址 record_id为get_domain_ip函数返回值
    @return: (状态代码 ,消息内容 ,记录时间) 元祖类型api返回值
    '''
    modify_url = "https://dnsapi.cn/Record.Modify"
    my_data = {"login_token":token,\
                "format":"json",\
                    "domain":domain ,\
                        "record_id": record_id,\
                            "value":new_ip,\
                                "record_type":domain_type,\
                                    "record_line_id":"10=0"}
    res = requests.post(url=modify_url ,data=my_data ,timeout=5)
    recv_data = json.loads(res.text)
    return (recv_data['status']['code'] ,recv_data['status']['message'] ,recv_data['status']['created_at'])

def main():
    local_ip = get_local_ip()
    record_id ,domain_ip = get_domain_ip()
    if local_ip != domain_ip:
        recv_data = modify_domain_ip(local_ip , record_id)
        if recv_data[0] == '1':
            log_data = recv_data[2] + "-->" + local_ip + " 更新记录值成功\r\n"
        else:
            log_data = recv_data[2] + "-->" + local_ip + " 记录更新失败\r\n"
        with open(log_file_path,"a")as f_log:
            f_log.writelines(log_data)

if __name__ == "__main__":
    #main()
    print(get_local_ip())