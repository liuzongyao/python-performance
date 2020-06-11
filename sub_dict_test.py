from common.log import logger, color


class Common():
    def __init__(self):
        super(Common, self).__init__()
        self.global_info = {}
        self.final_status = ["S", "F", "Running", "Error", "FAILURE", "failed", "FAIL",
                             "CreateError", "StartError"]
        self.result_set = {}

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




a = {"a":1,"b":2}
b = {"a":1,"b":2,"c":3}
c = {
    '欧美':{
        'www.youporn.com':['很多免费的，世界最大','质量一般'],
        'www.pornhub.com':['很多免费的，很大','质量比youpirn高点'],
        'letmedothistoyou.com':['多事自拍，高质量图片很多','资源不多，更新慢'],
        'x-art.com':['质量很高，真的很高','全部收费，屌丝请绕行']
    },
    '日韩':{
        'tokyo':['质量很高，个人已经不喜欢日韩范了','听说是收费的']
    },
    '大陆':{
        '1024':['全部免费，好人一生平安','服务器在国外，慢']
    }
}
d = {'日韩':{
        'tokyo':['质量很高，个人已经不喜欢日韩范了','听说是收费的吗']}}
# ## 用set来实现
# aa = set(a.items())     #{('a', 1), ('b', 2)}
# bb = set(b.items())     #{('a', 1), ('c', 3), ('b', 2)}
#
# print(aa.issubset(b.items()))      ## true
# print(aa.issubset(bb))             ## true
#
# print(type(c))
# print(type(d))
#
# # cc = set(c.items())
# dd = set(d.items())
#
# # print(dd.issubset(cc))

isss = Common()

print(isss.is_sub_dict(d,c))
