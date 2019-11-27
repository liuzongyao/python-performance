import os
import time
import requests
import re
import urllib3


def get_list_from_str(string, separator=','):
    if string is not None and string != '':
        return string.split(separator)


ENV = os.getenv("ENV", "int")
RESOURCE_PREFIX = os.getenv("RESOURCE_PREFIX",
                            "local").replace(".", "").replace("_",
                                                              "-").lower()[0:10]
if ENV == "int":
    # necessary
    API_URL = "https://10.0.128.76"
    REGION_NAME = "high"
    CALICO_REGION = "calico-new"
    OVN_REGION = "ovn"
    GLOBAL_REGION_NAME = "global"
    REGISTRY = "10.0.128.76:60080"
    IMAGE = "{}/alaudaorg/qaimages:helloworld".format(REGISTRY)
    GLOBAL_ALB_NAME = "alb2"
    DEFAULT_NS = "alauda-system"
    VM_IPS = "129.28.171.104;129.28.145.9;129.28.167.29;94.191.57.191"
    VM_USERNAME = "root"
    VM_PASSWORD = "alauda_qavm"
    VM_KEY = "./key.pem"
    # 必需,模板仓库的chart repo地址信息
    CHARTREPO_URL = "alauda-chart-incubator-new.ace-default.cloud.myalauda.cn/"
    CHARTREPO_TYPE = "http"
    CHARTREPO_USER = "7DO9QoLtDx1g"
    CHARTREPO_PASSWORD = "2wb4E1iydRj7"
    # devops
    JENKINS_URL = "http://10.0.128.76:32001"
    JENKINS_USERNAME = "admin"
    JENKINS_PASSWORD = "11d1a9fac3f5b2da4beb6b05fc143a2eb8"
    JENKINS_TOOL_NAME = 'local-ares-jenkins'
    # nfs服务器的地址
    NFS_IP = '10.0.128.115'
    NFS_PATH = '/exported/path'
    # 可用的存储类名称
    SC_NAME = "cephfs"
    USERNAME = "admin@alauda.io"
    PASSWORD = "password"
    OIDC_ISSUER_URL = os.getenv('OIDC_HOST',
                                'http://10.0.128.96:31532/auth/realms/master')
    OIDC_SECRET_ID = os.getenv('OIDC_SECRET_ID',
                               'f1223197-2ce1-4bf3-9e56-fc1eee94e6ca')
elif ENV == "staging":
    # necessary
    API_URL = "https://10.0.129.100"
    REGION_NAME = "high"
    CALICO_REGION = "calico"
    OVN_REGION = "ovn"
    GLOBAL_REGION_NAME = "global"
    REGISTRY = "10.0.129.100:60080"
    IMAGE = "{}/alaudaorg/qaimages:helloworld".format(REGISTRY)
    GLOBAL_ALB_NAME = "alb2"
    DEFAULT_NS = "alauda-system"
    VM_IPS = "129.28.187.165;129.28.168.13;94.191.74.43"
    VM_USERNAME = "root"
    VM_PASSWORD = "alauda_qavm"
    VM_KEY = "./key.pem"
    # 必需,模板仓库的chart repo地址信息
    CHARTREPO_URL = "alauda-chart-incubator-new.ace-default.cloud.myalauda.cn/"
    CHARTREPO_TYPE = "http"
    CHARTREPO_USER = "7DO9QoLtDx1g"
    CHARTREPO_PASSWORD = "2wb4E1iydRj7"
    # devops
    JENKINS_URL = "http://10.0.128.241:32001"
    JENKINS_USERNAME = "admin"
    JENKINS_PASSWORD = "113b33301b3cea32350e993538708f403b"
    JENKINS_TOOL_NAME = 'local-ares-jenkins'
    # nfs服务器的地址
    NFS_IP = '10.0.128.163'
    NFS_PATH = '/exported/path'
    # 可用的存储类名称
    SC_NAME = "cephfs"
    USERNAME = "admin@alauda.io"
    PASSWORD = "password"
    OIDC_ISSUER_URL = os.getenv('OIDC_HOST',
                                'http://10.0.128.96:31532/auth/realms/master')
    OIDC_SECRET_ID = os.getenv('OIDC_SECRET_ID',
                               'f1223197-2ce1-4bf3-9e56-fc1eee94e6ca')
elif ENV == "prod":
    pass
else:
    API_URL = os.getenv("API_URL", "https://10.0.128.76")
    REGION_NAME = os.getenv("REGION_NAME", "high")
    CALICO_REGION = os.getenv("CALICO_REGION", "calico")
    OVN_REGION = os.getenv("OVN_REGION", "ovn")
    GLOBAL_REGION_NAME = os.getenv("GLOBAL_REGION_NAME", "global")
    REGISTRY = os.getenv("REGISTRY")
    IMAGE = "{}/alaudaorg/qaimages:helloworld".format(REGISTRY)
    GLOBAL_ALB_NAME = os.getenv("GLOBAL_ALB_NAME", "alb2-name")
    DEFAULT_NS = os.getenv("DEFAULT_NS", "alauda-system")
    VM_IPS = os.getenv(
        "VM_IPS", "129.28.171.104;129.28.145.9;129.28.167.29;94.191.57.191")
    VM_USERNAME = os.getenv("VM_USERNAME", "root")
    VM_PASSWORD = os.getenv("VM_PASSWORD", "07Apples")
    VM_KEY = os.getenv("VM_KEY", "")
    JENKINS_URL = os.getenv("JENKINS_URL", "http://10.0.128.241:32001")
    JENKINS_USERNAME = os.getenv("JENKINS_USERNAME", "admin")
    JENKINS_PASSWORD = os.getenv("JENKINS_PASSWORD",
                                 "116d95cef15e36da4f85742000b5b2e058")
    JENKINS_TOOL_NAME = os.getenv("JENKINS_TOOL_NAME", 'jenkins')
    # 必需,模板仓库的chart repo地址信息
    CHARTREPO_URL = os.getenv("CHARTREPO_URL")
    CHARTREPO_TYPE = os.getenv("CHARTREPO_TYPE", "http")
    CHARTREPO_USER = os.getenv("CHARTREPO_USER", "chartmuseum")
    CHARTREPO_PASSWORD = os.getenv("CHARTREPO_PASSWORD", "chartmuseum")
    # nfs服务器的地址
    NFS_IP = os.getenv('NFS_IP', '10.0.128.163')
    NFS_PATH = os.getenv('NFS_PATH', '/exported/path')
    # 可用的存储类名称
    SC_NAME = os.getenv("SC_NAME", "cephfs")
    USERNAME = os.getenv("USERNAME", "admin@alauda.io")
    PASSWORD = os.getenv("PASSWORD", "password")
    OIDC_ISSUER_URL = os.getenv('OIDC_HOST',
                                'http://10.0.128.96:31532/auth/realms/master')
    OIDC_SECRET_ID = os.getenv('OIDC_SECRET_ID',
                               'f1223197-2ce1-4bf3-9e56-fc1eee94e6ca')
if ENV in ("int", "staging", "prod"):
    PROXY = {
        "http": "http://alauda:RwL6%25hLM%25F8T*kLR@139.186.17.154:47586/",
        "https": "http://alauda:RwL6%25hLM%25F8T*kLR@139.186.17.154:47586/"
    }
else:
    PROXY = {}
# devops
HARBOR_URL = os.getenv("HARBOR_URL", "http://10.0.128.96:31104")
HARBOR_USERNAME = os.getenv("HARBOR_USERNAME", "admin")
HARBOR_PASSWORD = os.getenv("HARBOR_PASSWORD", "Harbor12345")
HARBOR_PROJECT = os.getenv("HARBOR_PROJECT", "e2e-automation")
GITLAB_URL = os.getenv("GITLAB_URL", "http://10.0.128.96:31101")
GITLAB_USERNAME = os.getenv("GITLAB_USERNAME", "root")
GITLAB_PASSWORD = os.getenv("GITLAB_PASSWORD", "WojzwaBxGqEHx-7xucx4")
GITLAB_ACCOUNT = 'root'
SONAR_URL = os.getenv("SONAR_URL", "http://10.0.128.96:32010")
SONAR_USERNAME = os.getenv("SONAR_USERNAME", "admin")
SONAR_PASSWORD = os.getenv("SONAR_PASSWORD",
                           "89141cf4ea9503bfde5f60432895997321a9fe71")
DOCKER_REGISTRY_URL = os.getenv("DOCKER_REGISTRY_URL",
                                "http://10.0.128.241:32677")
# not necessary
TESTCASES = os.getenv("TESTCASES", "")
CASE_TYPE = os.getenv("CASE_TYPE", "BAT")
PROJECT_NAME = "e2eproject"
K8S_NAMESPACE = "e2enamespace"
CALICO_PROJECT_NAME = "e2eproject-calico"
GLOBAL_INFO_FILE = "./temp_data/global_info{}.json".format(os.getpid())
RECIPIENTS = get_list_from_str(os.getenv("RECIPIENTS", "testing@alauda.io"))
# 腾讯的key
SECRET_ID = "AKID84kBMHwKUP4VggjwBAKFvxlJcgU3frtg"
SECRET_KEY = "aDlNSjBSZGRPdkxXUjZWZ2JHZnFPaGpXMklJa3d0WjA="

# 重试次数
RERUN_TIMES = int(os.getenv("RERUN_TIMES", 0))
# 进程数
THREAD_NUM = os.getenv("THREAD_NUM", "3")
# 日志级别和存储位置
LOG_LEVEL = "INFO"
LOG_PATH = "./report"
# 邮件服务器地址
SMTP = {
    'host': os.getenv('SMTP_HOST', 'smtp.163.com'),
    'port': os.getenv('SMTP_PORT', 465),
    'username': os.getenv('SMTP_USERNAME', '15830736131@163.com'),
    'password': os.getenv('SMTP_PASSWORD', '07Apples'),
    'sender': os.getenv('EMAIL_FROM', '15830736131@163.com'),
    'debug_level': 0,
    'smtp_ssl': True
}
# 资源鉴权
LDAP_HOST = os.getenv('LDAP_HOST', '10.0.128.96:30435')


def get_token(idp_name='local', username=USERNAME, password=PASSWORD):
    url = API_URL + "/console-acp/api/v1/token/login"
    urllib3.disable_warnings()
    r = requests.get(url, verify=False, timeout=15, proxies=PROXY)
    auth_url = r.json()["auth_url"]
    auth_path = '/'.join(auth_url.split("/")[-2:])
    auth_url = API_URL + '/' + auth_path
    r = requests.get(auth_url, verify=False, timeout=15, proxies=PROXY)
    content = r.text
    req = re.search('req=[a-zA-Z0-9]{25}', content).group(0)[4:]
    url = API_URL + "/dex/auth/{}?req=".format(idp_name) + req
    params = {"req": req, "login": username, "password": password}

    response = requests.post(
        url, params=params, verify=False, timeout=10, proxies=PROXY)
    content = response.history[1].text

    code = re.search('[a-zA-Z0-9]{25}', content).group(0)
    url = API_URL + "/console-acp/api/v1/token/callback?code={}&state=alauda-console".format(
        code)

    r = requests.get(url, verify=False, timeout=10, proxies=PROXY)
    token = r.json()['id_token']
    token_type = r.json()['token_type']
    auth = "{} {}".format(token_type.capitalize(), token)
    return auth


# 发送请求的headers
headers = {"Content-Type": "application/json", "Authorization": get_token()}


def get_audit():
    payload = {"page": 1, "page_size": 20, "user_name": USERNAME}
    current_time = int(time.time())
    times = {"start_time": current_time - 1800, "end_time": current_time}
    payload.update(times)
    url = API_URL + "/v1/kubernetes-audits"
    urllib3.disable_warnings()
    result = requests.get(
        url, params=payload, proxies=PROXY, headers=headers, verify=False)
    if result.status_code != 200 or result.json().get('total_items') == 0:
        return True
    return False


# 获取是否有审计
# AUDIT_UNABLED = get_audit()
AUDIT_UNABLED = True
