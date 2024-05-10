# 0x02 未授权服务暴露面管理系统

使用前注意事项：

禁止使用该工具对未授权的系统或网站进行渗透测试


开发缘由：

对于中小企业来说，可能没有专业的安全工程师，导致线上各种外网服务均暴露在外网，部分服务还存在弱口令和未授权访问的问题，很容易被攻击者所利用。

可以快速采用 Nmap+Masscan 相结合的方式来实现服务巡检


开发思路：

1.添加需要检测的 IP

2.添加相应的计划任务，定期巡检


相关技术：

基于 Python 3.8 +Flask+ Mysql


todo:

1.支持 xlsx 格式导入

2.支持发现 未授权访问 的服务通过 钉钉、飞书，企业微信报警

3.支持查看扫描日志

4.支持 docker 部署

项目地址：[https://github.com/menglike/ServiceFound](https://github.com/menglike/ServiceFound)

部署方案：

1. 下载源码到本地

`git clone ``https://github.com/menglike/ServiceFound`

1. 安装相应的第三方库

`pip install -r requirements.txt`

1. 配置数据库信息

配置文件：conf/config.py ,可以将 sql 文件导入到本地数据库中

1. 启动服务

`python main.py`

默认启动端口为 8000，可以根据实际情况进行修改,

默认登录账户 secw / 123

5.访问系统

在浏览器中访问 [http://127.0.0.1](http://127.0.0.1:8000)

![](static/GBHmbfNn8oyb5Sxo5AZcPBvrnGb.png)

6.登录成功后，查看 IP 列表

![](static/W6OVbfZvloefyNxEgnmcf4Icnbh.png)

7.查看所有的被识别的服务

![](static/YzpPboJXuosMffxaycVc1OcQnuf.png)
