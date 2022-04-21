#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Time  : 2022/1/20 
# @Author: Hans_q
# @Email : hans_q@bupt.edu.cn
import argparse

import requests
import json
import datetime
from lxml import etree

header={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Connection': 'close'
}

def login(username, password):
    '''
    根据用户名和密码进行登录, 获取服务器返回的cookies
    :param username: 你的学号
    :param password: 你的登录密码（研究生身份证后八位）
    :return:
    '''
    url = 'https://auth.bupt.edu.cn/authserver/login'
    data_dict = {"username": username,
                 "password": password,
                 "type": "username_password",
                 "submit": "登录",
                 "_eventId" : "submit"}

    session = requests.session()
    response1 = session.get(url=url,headers=header,verify=False)

    html = etree.HTML(response1.text)
    execution = html.xpath('//*[@id="loginForm"]/div[5]/input[2]/@value')[0]
    data_dict['execution'] = execution

    response2 = session.post(url=url, data=data_dict, headers= header,verify=False)
    if response2.status_code != 200:
        raise Exception(f'登录失败！http状态码:{response2.status_code}, 请检查用户名和密码')

    return session

def get_old_info(session):
    '''
    获取oldinfo
    :param cookies:
    :return:
    '''
    url = "https://app.bupt.edu.cn/ncov/wap/default/index?from=singlemessage&isappinstalled=0"
    resp = session.get(url,headers=header,verify=False)
    content = resp.text # 是html字符串（网页源码）

    str1 = content.split("oldInfo: ")[-1]
    str2 = str1.split("tipMsg:")[0]
    oldinfo_str = str2.split(",\n")[0]

    return session, json.loads(oldinfo_str)

def submit(session, oldinfo):
    '''
    更新日期, 提交newinfo
    :param cookies:
    :return:
    '''
    url = 'https://app.bupt.edu.cn/ncov/wap/default/save'

    info = {
        "ismoved": "0", # 是否移动过
        "jhfjrq": "",   # 计划返京日期（隐藏了）
        "jhfjjtgj": "", # 计划返京交通工具
        "jhfjhbcc": "", # 计划返京航班车次
        "szgj": "",     # 所在国家（隐藏了）
        "szcs": "",     # 所在城市
        "zgfxdq": "0",  # 在不在高风险地区
        "mjry": "0",    # 是否密接人员
        "csmjry": "0",  # 场所密集人员
        "ymjzxgqk": "\u5168\u90e8\u63a5\u79cd", #疫苗接种相关情况 （Unicode编码：全部接种）
        "xwxgymjzqk": "3",  #校外接种情况 3针
        "tw": "2",      # 体温 第二档
        "sfcxtz": "0",  # 是否发热
        "sfjcbh": "0",  # 是否接触疑似感染人群
        "sfcxzysx": "0",# 是否有其他注意的情况
        "qksm": "",     # 情况说明
        "sfyyjc": "0",  # 是否医院检查
        "jcjgqr": "0",  # 检查结果
        "remark": "",   # 其他信息
        "address": "",
        "geo_api_info": "{\"type\":\"complete\",\"position\":{\"Q\":31.627663845487,\"R\":113.47805067274402,\"lng\":113.478051,\"lat\":31.627664},\"location_type\":\"html5\",\"message\":\"Get geolocation success.Convert Success.Get address success.\",\"accuracy\":600,\"isConverted\":true,\"status\":1,\"addressComponent\":{\"citycode\":\"0722\",\"adcode\":\"421303\",\"businessAreas\":[],\"neighborhoodType\":\"\",\"neighborhood\":\"\",\"building\":\"\",\"buildingType\":\"\",\"street\":\"\",\"streetNumber\":\"\",\"country\":\"\u4e2d\u56fd\",\"province\":\"\u6e56\u5317\u7701\",\"city\":\"\u968f\u5dde\u5e02\",\"district\":\"\u66fe\u90fd\u533a\",\"towncode\":\"421303100000\",\"township\":\"\u6dc5\u6cb3\u9547\"},\"formattedAddress\":\"\u6e56\u5317\u7701\u968f\u5dde\u5e02\u66fe\u90fd\u533a\u6dc5\u6cb3\u9547\u8679\u6865\u6751\",\"roads\":[],\"crosses\":[],\"pois\":[],\"info\":\"SUCCESS\"}",
        "area": "\u6e56\u5317\u7701 \u968f\u5dde\u5e02 \u66fe\u90fd\u533a", # 湖北省 随州市 曾都区
        "province": "\u6e56\u5317\u7701",   # 湖北省
        "city": "\u968f\u5dde\u5e02",       # 随州市
        "sfzx": "0",    # 是否在校
        "sfjcwhry": "0",# 是否接触过武汉
        "sfjchbry": "0",# 湖北其他地区
        "sfcyglq": "0", # 是否观察期
        "gllx": "",     # 观察地点
        "glksrq": "",   # 观察开始时间
        "jcbhlx": "",   # 接触人群类型（疑似、确诊）
        "jcbhrq": "",   # 接触日期
        "bztcyy": "",   # 不在同城的原因 1234：其他探亲旅游回家
        "sftjhb": "0",  # 是否经停湖北其他地区
        "sftjwh": "0",  # 是否经停武汉
        "sfsfbh": "0",  # 是否跨省了
        "xjzd": "\u6e56\u5317\u6b66\u6c49", # 现居住地 湖北武汉
        "jcwhryfs": "", # 接触方式
        "jchbryfs": "",
        "szsqsfybl": "0",# 所在社区是否有确诊病例
        "sfygtjzzfj": 0, # 家中是否有共同居住者返京
        "gtjzzfjsj": "",
        "sfjzxgym": "1",   # 是否已接种第一针新冠疫苗
        "sfjzdezxgym": "1",# 是否已接种第二针新冠疫苗
        "jcjg": "",        # 检查结果
        "date": "20220119",# 日期！！！
        "uid": "31612",     # 好像是个死的值 每个人似乎不一样！！1
        "created": 1642521842, # 不懂
        "jcqzrq": "",
        "sfjcqz": "",
        "sfsqhzjkk": 0,
        "sqhzjkkys": "",
        "fxyy": "\u4e00\u76f4\u5728\u6821", # 返校原因
        "created_uid": 0,
        "id": 16971743
    }

    today_str = datetime.datetime.now().strftime("%Y%m%d")
    oldinfo["date"] = today_str

    response = session.post(url=url, data=oldinfo, headers=header,verify=False)
    return json.loads(response.text)

def load_config():
    '''
    读取配置文件里的学号和密码
    :return:
    '''
    with open("user.config") as f:
        config = json.load(f)
        username = config['username']
        password = config['password']

        return username, password

def get_params():
    '''
    获取用户输入的 用户名和密码
    '''
    #获取对象
    parser = argparse.ArgumentParser(description='get_input_params')
    #设置参数
    parser.add_argument('-u','--username', help='学号')
    parser.add_argument('-p','--password', help='密码')
    #获取参数
    args = parser.parse_args()
    return args.username, args.password

if __name__ == "__main__":

    # username, password = load_config()
    username, password = get_params()   # 从github secrets里获取用户名和密码
    session = login(username, password)
    session2, old_info = get_old_info(session)
    result = submit(session2, old_info)

    if(result['e']==0):
        print("今日填报成功!")
    else:
        print("提示信息：", result['m'])

