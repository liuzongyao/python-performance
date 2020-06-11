# coding=utf-8
import codecs
import jinja2
import json
import os
import yaml
import sys
from subprocess import getstatusoutput
from time import sleep, time
from common import settings
from common.api_requests import AlaudaRequest
from common.exceptions import ResponseError, ParseResponseError
from common.loadfile import FileUtils
from common.log import logger, color


class Common(AlaudaRequest):
    def __init__(self):
        super(Common, self).__init__()
        self.global_info = {}
        self.final_status = ["S", "F", "Running", "Error", "FAILURE", "failed", "FAIL",
                             "CreateError", "StartError"]
        self.result_set = {}

    def genetate_global_info(self):
        self.global_info = FileUtils.load_file(self.global_info_path)

    def generate_data(self, file_path, data={}):
        """
        对指定文件替换数据，生成最终测试数据
        :param file_path: 指定测试文件路径
        :param data: 需要替换的数据，传入字典类型，key为文件中被替换的内容，value为替换的字符串
        :return: 最终测试数据 类型是字符串
        """
        self.global_info.update(data)
        content = json.dumps(FileUtils.load_file(file_path))
        for key in self.global_info:
            if isinstance(self.global_info[key], str):
                content = content.replace(key, self.global_info[key])
        return content

    def generate_jinja_template(self, filename):
        with codecs.open(filename, "r", encoding="utf-8") as fp:
            body_data = fp.read()
        return jinja2.Template(body_data)

    def generate_jinja_data(self, filename, data={}):
        with codecs.open(filename, "r", encoding="utf-8") as fp:
            body_data = fp.read()
        template = jinja2.Template(body_data)
        data.update({"default_label": settings.DEFAULT_LABEL})
        result = template.render(data)
        result = result.replace("None", "null").replace("\"null\"", "None").replace("'null'", "None")
        result = result.replace("\t", " ")
        return yaml.safe_load(result)

    def make_file(self, file, data):
        with open(file, "r") as f:
            content = f.read()
        for key in data:
            content = content.replace(key, data[key])
        filename = file.split("/")[-1]
        if not os.path.exists("temp_data"):
            os.mkdir("temp_data")
        to_file = "temp_data/" + filename
        with open(to_file, "w") as f:
            f.write(content)
        return to_file

    @staticmethod
    def get_value(json_content, query, delimiter='.'):
        """ Do an xpath-like query with json_content.
        @param (json_content) json_content
            json_content = {
                "ids": [1, 2, 3, 4],
                "person": {
                    "name": {
                        "first_name": "Leo",
                        "last_name": "Lee",
                    },
                    "age": 29,
                    "cities": ["Guangzhou", "Shenzhen"]
                }
            }
        @param (str) query
            "person.name.first_name"  =>  "Leo"
            "person.cities.0"         =>  "Guangzhou"
        @return queried result
        """
        if json_content == "" or json_content == []:
            raise ResponseError("response content is {}!".format(json_content))

        try:
            for key in query.split(delimiter):
                if isinstance(json_content, list):
                    json_content = json_content[int(key)]
                elif isinstance(json_content, dict):
                    json_content = json_content[key]
                else:
                    raise ParseResponseError(
                        "response content is in text format! failed to query key {}!, json_content {}".format(key,
                                                                                                              json_content))
        except (KeyError, ValueError, IndexError):
            logger.error(color.red("query is {}, json_content is {}".format(key, json_content)))
            raise ParseResponseError("failed to query json when extracting response! response: {}".format(json_content))

        return json_content

    @staticmethod
    def get_value_list(data, query, list_delimiter='||', delimiter='.'):
        """
        get value from dict or list
        :param data: 需要被解析的数据
        :param keys: 通过这些keys来解析数据,如果字典传key，如果数据传下标
        :example data = {"key1":{"key2":[{"key3":"key4"},{"key3":"key5"}]}}
        期望获取到key4的值 keys = ["key1","key2", 0, "key3"]
        """
        keys = query.split(list_delimiter)
        if len(keys) > 1:
            value = Common.get_value(data, delimiter.join(keys[0:-1]), delimiter=delimiter)
            list_data = value
        else:
            list_data = data
        ret_list = []
        for data in list_data:
            # ret_list.append(data[keys[-1]])
            ret_list.append(Common.get_value(data, keys[-1], delimiter=delimiter))
        return ret_list

    @staticmethod
    def generate_time_params():
        current_time = int(time())
        return {"start_time": current_time - 1800, "end_time": current_time}

    def get_status(self, url, key, expect_value, delimiter='.', params={"project_name": settings.PROJECT_NAME},
                   expect_cnt=10):
        """
        :param url: 获取服务或者构建详情的url
        :param key: 获取状态的key 需要是个string，传入层级的key
        :param expect_value:最终判断状态
        :return: true or false
        """
        cnt = 0
        flag = False
        # error_cnt = 0
        expect_values = expect_value.split("||")
        while cnt < expect_cnt and not flag:
            cnt += 1
            response = self.send(method="GET", path=url, params=params)
            assert response.status_code == 200, "get status failed"
            try:
                value = self.get_value(response.json(), key, delimiter)
            except ParseResponseError:
                logger.error("response content has no query key")
                sleep(5)
            else:
                logger.info(value)
                for expect_value in expect_values:
                    if value == expect_value:
                        flag = True
                        break
                # 因为devops应用会获取pod状态 如果pod失败会是失败状态，但是pod自动重启后可以成功启动
                # if value in ("Failed"):
                #     error_cnt += 1
                #     if error_cnt == 5:
                #         break
                sleep(5)
        return flag

    def get_logs(self, url, expect_value, times=10):
        cnt = 0
        flag = False
        while cnt < times and not flag:
            cnt += 1
            params = Common.generate_time_params()
            params.update({"project_name": self.project_name})
            response = self.send(method="GET", path=url, params=params)
            assert response.status_code == 200, "get log failed"
            logger.info("log: {}".format(response.text))
            if expect_value in response.text:
                flag = True
                break
            sleep(5)
        return flag

    def get_uuid_accord_name(self, contents, name, uuid_key):
        """
        :param contents: 通过返回体获取到的列表数组 [{"key":""value"...},{"key":""value"...}...]
        :param name: 资源名称的一个字典:{"name": "resource_name"}
        :param uuid_key: 资源uuid的key
        :return: 资源的uuid
        """

        if type(contents).__name__ == 'list':
            for content in contents:
                for key, value in name.items():
                    if content[key] == value:
                        return content[uuid_key]
        elif type(contents).__name__ == 'dict':
            for key, value in name.items():
                if contents[key] == value:
                    return contents[uuid_key]
        return ""

    def update_result(self, result, flag, case_name):
        """
        如果是非block的验证点，先将结果更新到result内，在最后判断case的执行结果
        :param result: 最终用来判断case执行成功与失败的集合 :{"flag":True/False, case_name: "failed"}
        :param flag: True/False
        :param error_name: case的名称
        :return: result
        """
        if not flag:
            result['flag'] = False
            result.update({case_name: "failed"})
        return result

    def check_search_different_level_key(self, url, payload, count, keys, search_type1, key1, search_type2, key2):
        """
        用来校验用不同级的搜索条件搜索日志或事件类型的数据，搜索结果是否正确
        count: 接口中对应的返回数据条数key值
        keys: 用来表示返回数据中的results,比如日志就是'logs'
        search_type1: 第一个查询条件
        key1: 第一个查询条件对应接口返回数据中的key值，类型为''
        search_type2: 第二个查询条件
        key2： 第二个查询条件对应接口返回数据中的key值，类型为''
        :return:
        """
        cnt = 0
        flag = False
        while cnt < 15:
            cnt += 1
            payload.update(self.generate_time_params())
            results = self.send(method='get', path=url, params=payload)
            if results.status_code == 200 and self.get_value(results.json(), count) > 0:
                flag = True
                result = self.get_value(results.json(), keys)
                for i in range(len(result)):
                    if self.get_value(result[i], key1) != search_type1 or self.get_value(result[i],
                                                                                         key2) != search_type2:
                        flag = False
                break
            sleep(3)
        return flag

    def check_search_single_key(self, url, payload, count, keys, search_type, key):
        """
        用来校验用一个搜索条件搜索日志或事件类型的数据，搜索结果是否正确
        count: 接口中对应的返回数据条数key值
        keys: 用来表示返回数据中的results,比如日志就是'logs'
        search_type: 查询条件
        key: 查询条件对应接口返回数据中的key值，类型为''
        :return:
        """
        cnt = 0
        flag = False
        while cnt < 15:
            cnt += 1
            payload.update(self.generate_time_params())
            results = self.send(method='get', path=url, params=payload)
            if results.status_code == 200 and self.get_value(results.json(), count) > 0:
                flag = True
                result = self.get_value(results.json(), keys)
                for i in range(len(result)):
                    if self.get_value(result[i], key) != search_type:
                        flag = False
                break
            sleep(3)
        return flag

    def search_audit(self, payload):
        """
        获取平台审计
        :param payload: 检索条件{"user_name": "admin@alauda.io","operation_type":
                                "create","resource_type": "notifications","resource_name": self.notification_name}
        :return: 返回审计信息
        """
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        count = 0
        payload.update({"page": 1, "page_size": 200})
        while count < 30:
            count += 1
            url = "v1/kubernetes-audits"
            payload.update(self.generate_time_params())
            result = self.send(method='get', path=url, params=payload)
            if result.status_code == 200 and self.get_value(result.json(), 'total_items') > 0 and payload['resource_name'] in result.text:
                break
            sleep(3)
        return result

    def get_kevents(self, payload, expect_value='', times=0, index=0):
        """
        获取操作的k8s事件
        :param index: 事件下标
        :param times: 期望出现的字符串次数
        :param expect_value: 期望出现的对应字符串
        :param payload: 检索条件，必填项{"cluster":region}可选填name，namespace，kind
        :return: 返回事件信息
        """
        import re
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < 20:
            cnt += 1
            url = "v4/events"
            payload.update(self.generate_time_params())
            result = self.send(method='get', path=url, params=payload)
            if result.status_code == 200 and self.get_value(result.json(), 'total_items') > 0:
                if expect_value:
                    count = int(self.get_value(result.json(), "items.{}.spec.detail.event.count".format(index)))
                    if len(re.findall(expect_value, result.text)) * count >= times:
                        flag = True
                        break
                    else:
                        sleep(5)
                        continue
                else:
                    flag = True
                    break
            sleep(5)
        if not flag:
            logger.error("获取事件失败:{}".format(result.text))
        return flag

    def check_exists(self, url, expect_status, params={"project_name": settings.PROJECT_NAME}, expect_cnt=10):
        """
        主要用于判断资源是否存在
        :param expect_cnt: 循环几次
        :param params: 需要携带的参数
        :param url: 获取资源的url
        :param expect_status: 期望返回的code
        :return:
        """
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < expect_cnt and not flag:
            cnt += 1
            response = self.send(method="GET", path=url, params=params)
            if response.status_code == expect_status:
                flag = True
                break
            sleep(5)
        return flag

    def check_value_in_response(self, url, value, params=None, expect_cnt=10):
        """
        主要用于判断创建后的资源是否在资源列表中，
            个别资源创建后会延时出现在列表中，需要循环获取
        :param params: 需要带上的参数
        :param expect_cnt: 循环几次
        :param url: 获取资源列表的url
        :param value: 资源名称
        :return:
        """
        if params is None:
            params = {"project_name": settings.PROJECT_NAME}
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < expect_cnt and not flag:
            cnt += 1
            response = self.send(method="GET", path=url, params=params)
            assert response.status_code in (200, 404), "get list failed"
            if value in response.text:
                flag = True
                break
            sleep(5)
        return flag

    def excute_script(self, cmd, ip, use_key=True, user=settings.VM_USERNAME):
        """
        主要用于远程在虚拟机执行脚本
        :param cmd: 远程需要执行的命令
        :param ip：虚拟机IP
        :return:
        """
        if settings.VM_KEY and use_key:
            remote_cmd = "chmod 400 {key};ssh -i {key} -o StrictHostKeyChecking=no {user}@{ip} '{cmd}'".format(
                key=settings.VM_KEY,
                user=user,
                ip=ip, cmd=cmd)
        else:
            remote_cmd = "sshpass -p {passwd} ssh -o StrictHostKeyChecking=no {user}@{ip} '{cmd}'".format(
                passwd=settings.VM_PASSWORD,
                user=user,
                ip=ip, cmd=cmd)
        logger.info("excute cmd is :{}".format(remote_cmd))
        result = getstatusoutput(remote_cmd)
        logger.info("excute cmd result is {}".format(result))
        return result

    def resource_pagination(self, url, query="results.0.name", page_size_key="page_size",
                            params={"project_name": settings.PROJECT_NAME}):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        params.update({page_size_key: 1, "page": 1})
        page1 = self.send(method="GET", path=url, params=params)
        if page1.status_code != 200:
            return False
        logger.info("列表1的结果:{}".format(page1.json()))
        name1 = self.get_value(page1.json(), query)
        params.update({page_size_key: 1, "page": 2})
        page2 = self.send(method="GET", path=url, params=params)
        if page2.status_code != 200:
            return False
        logger.info("列表2的结果:{}".format(page2.json()))
        name2 = self.get_value(page2.json(), query)
        if name1 == name2:
            return False
        return True

    def get_k8s_resource_data(self, data, name, list_key="results"):
        '''
        只适用于通过Kubernetes资源列表返回对应名称资源的信息
        :param data:列表的json信息
        :param name:对应的资源名称
        :param list_key:获取到列表信息中列表数据的key
        :return:返回对应资源的信息
        '''
        contents = self.get_value(data, list_key)
        for content in contents:
            if name in str(content):
                return content
        return {}

    def _sub_dict(self, sub, sources):
        '''
        用于判断sub的数据是否在sources都存在，即判断sub是否是sources的子集
        :param sub: 期望数据
        :param sources: 返回数据
        :return: 如果期望数据都在返回数据里返回true，反之false
        '''

        if type(sub) != type(sources):
            self.result_set.update({'result': False,
                                    'message': "比对数据的格式不一样:sub type:{}, rep type:{}"
                                   .format(type(sub), type(sources))})
            return False

        if isinstance(sub, dict):
            for k, v in sub.items():
                if isinstance(v, str):
                    if k in sources:
                        if v and v not in str(sources[k]):
                            self.result_set.update({'result': False,
                                                    'message': "对比数据中不包含预期的子资, "
                                                               "子资源键: {}, 值:{},实际数据:{}"
                                                   .format(k, v, sources[k])})
                            return False
                    else:
                        self.result_set.update({'result': False,
                                                'message': "对比数据中不包含预期的子资, "
                                                           "子资源键: {}, 值:{},实际数据:{}"
                                               .format(k, v, sources)})
                        return False
                elif isinstance(v, list):
                    if k in sources:
                        if self._sub_dict(v, sources[k]) is False:
                            # self.result_set.update({'result': False, 'message': "期望数据:{},实际数据:{}"
                            #                        .format(v, sources[k])})
                            return False
                    else:
                        self.result_set.update({'result': False,
                                                'message': "对比数据中不包含预期的子资, "
                                                           "子资源键: {}, 值:{},实际数据:{}"
                                               .format(k, v, sources)})
                        return False
                elif isinstance(v, dict):
                    if k in sources:
                        if v and self._sub_dict(v, sources[k]) is False:
                            return False
                    else:
                        self.result_set.update({'result': False,
                                                'message': "对比数据中不包含预期的子资, "
                                                           "子资源键: {}, 值:{},实际数据:{}"
                                               .format(k, v, sources)})
                        return False
        elif isinstance(sub, list):
            result = True
            for ind, value in enumerate(sub):
                for s_ind, s_value in enumerate(sources):
                    if type(value) != type(s_value):
                        self.result_set.update({'result': False, 'message': "比对数据的格式不一样:sub type:{}, rep type:{}"
                                               .format(type(sub), type(sources))})
                        return False
                    if isinstance(value, str) and value not in sources:
                        self.result_set.update({'result': False,
                                                'message': "对比数据中不包含预期的子资:子资源索引: {}, 值:{}, 对比数据:{}"
                                               .format(ind, value, sources)})
                        return False
                    elif isinstance(value, dict):
                        result = self._sub_dict(value, s_value)
                        if result:
                            break
                    elif isinstance(value, list):
                        result = self._sub_dict(value, s_value)
                        if result:
                            break
                else:
                    if not result:
                        self.result_set.update({'result': False})
                        return False
        elif isinstance(sub, str):
            if sub != sources:
                self.result_set.update({'result': False, 'message': "数据比对失败,期望值:{},实际值:{}"
                                       .format(sub, sources)})
                return False
        self.result_set.update({'result': True, 'message': ''})
        return True

    def is_sub_dict(self, sub, sources):
        self._sub_dict(sub, sources)
        if self.result_set.get('result'):
            return True
        else:
            logger.error(color.red(self.result_set.get('message')))
            return False

    def is_sub_list(self, values1, values2):
        '''
        比对列表values1是不是value2的子集
        :param values1: 期望数据
        :param values2: 实际数据
        :return: 如果期望数据都在实际数据里返回true，反之false
        '''
        flag = True
        if isinstance(values1, list) and isinstance(values2, list) and len(values2) >= len(values1):
            for value1 in values1:
                for value2 in values2:
                    if self.is_sub_dict(value1, value2):
                        values2.remove(value2)
                        flag = True
                        break
                    logger.error(color.red("数据比对失败,期望值:{},实际值:{}".format(value1, value2)))
                    flag = False
                if not flag:
                    return flag
            return True
        logger.error("value1不是value2的子集，value1长度是:{},value2长度是:{}".format(len(values1), len(values2)))
        return False
