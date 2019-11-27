import settings
from locust import HttpLocust, TaskSet, task, between


class UserBehavior(TaskSet):

    # def on_start(self):
    #     """ on_start is called when a Locust start before any task is scheduled """
    #     self.login()
    #
    # def on_stop(self):
    #     """ on_stop is called when the TaskSet is stopping """
    #     self.logout()
    #
    # def login(self):
    #     self.client.post("/login", {"username":"admin@alauda.io", "password":"password"})
    #
    # def logout(self):
    #     self.client.post("/logout", {"username":"ellen_key", "password":"education"})

    # @task(2)
    # def index(self):
    #     self.client.get("/")

    def __init__(self, parent):
        TaskSet.__init__(self, parent)
        self.endpoint = settings.API_URL
        self.region_name = settings.REGION_NAME
        self.calico_region = settings.CALICO_REGION
        self.k8s_namespace = settings.K8S_NAMESPACE
        self.project_name = settings.PROJECT_NAME
        self.default_ns = settings.DEFAULT_NS
        self.global_info_path = settings.GLOBAL_INFO_FILE
        self.proxy = settings.PROXY
        self.headers = settings.headers

    @task(1)
    def profile(self):
   
        self.client.get('/devops/api/v1/imagerepository/aa-liuzongyao', headers=self.headers, proxies=self.proxy)

    @task(2)
    def trigger(self):
        self.client.post('/devops/api/v1/pipelineconfig/aa-liuzongyao/demo1235/trigger', data='{}', headers=self.headers,
                         proxies=self.proxy)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5, 10)

