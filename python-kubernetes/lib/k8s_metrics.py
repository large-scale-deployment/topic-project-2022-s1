import json
from kubernetes import client
from kubernetes.utils import quantity
from humanfriendly import format_size
from numpy import NaN

# my libs
from lib import utils, k8s_deployments, k8s_pods

class DeploymentResourceStatsEncoder(json.JSONEncoder):

    def default(self, o):
        return dict(
            app_name=o._app_name,
            cpu_usage=o.cpu_usage(),
            memory_usage=o.memory_usage(),
            cpu_limit = o.cpu_limit(),
            memory_limit = o.memory_limit()
            )

class DeploymentResourceStats(object):
    def __init__(self, app_name):
        super().__init__()
        self._app_name = app_name
        self._metrics = []

    def add_metric_from_containers(self, pod_name, limits, usage):
        cpu_usage = usage['cpu'] * 1000
        memory_usage = usage['memory']
        cpu_limit = limits['cpu'] * 1000
        memory_limit = limits['memory']

        self._metrics.append(dict(
            name = pod_name,
            cpu_limit = cpu_limit,
            memory_limit = memory_limit,
            cpu_usage = cpu_usage,
            memory_usage = memory_usage
        ))

    def cpu_usage(self):
        cpu = 0
        for metric in self._metrics:
            cpu += metric['cpu_usage']
        return cpu

    def memory_usage(self, value=False):
        memory = 0
        for metric in self._metrics:
            memory += metric['memory_usage']

        if value:
            return memory
        else:
            return format_size(memory, binary=True)

    def cpu_limit(self):
        cpu = 0
        for metric in self._metrics:
            cpu += metric['cpu_limit']

        return cpu

    def memory_limit(self, value=False):
        memory = 0
        for metric in self._metrics:
            memory += metric['memory_limit']

        if value:
            return memory
        else:
            return format_size(memory, binary=True)

    def cpu_rate(self):
        if self.cpu_limit() == 0:
            return NaN
        else:
            return round(self.cpu_usage()/self.cpu_limit(), 2)

    def memory_rate(self):
        if self.memory_limit(True) == 0:
            return NaN
        else:
            return round(self.memory_usage(True)/self.memory_limit(True), 2)

    def __repr__(self):
        tmp = f'app: {self._app_name}, cpu/memory rate: {self.cpu_rate()}/{self.memory_rate()}, cpu/memory usage: {round(self.cpu_usage(), 2)}/{self.memory_usage()}, cpu/memory limit: {self.cpu_limit()}/{self.memory_limit()}'
        for pod in self._metrics:
            tmp += '\n  ' + f"{pod['name']}, cpu: {round(pod['cpu_usage'], 2)}, memory: {format_size(pod['memory_usage'], binary=True)}"
        return tmp


    def __str__(self):
        return self.__repr__()

def get_resource_usage_object_by_pod(pod_name, namespace):
    # kubectl get --raw "/apis/metrics.k8s.io/v1beta1/nodes"
    # https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/
    apiCustObject = client.CustomObjectsApi()
    cust_params = dict(
        group="metrics.k8s.io",version="v1beta1",
        namespace=namespace, plural="pods",
        name = pod_name
    )
    return apiCustObject.get_namespaced_custom_object(**cust_params)

def get_resource_usage_object_by_deployment(name, namespace):
    deployment = k8s_deployments.get_deployment_by_name(name, namespace)
    return get_resource_usage_by_deployment(deployment)

def get_resource_usage_by_deployment(deployment):
    apiCustObject = client.CustomObjectsApi()
    dname = deployment.metadata.name
    label_selector = utils.construct_label_selectors(deployment)
    namespace = deployment.metadata.namespace
    kwargs = dict(
        group="metrics.k8s.io",version="v1beta1", 
        namespace=namespace, plural="pods",
        label_selector=label_selector
    )
    resource = apiCustObject.list_namespaced_custom_object(**kwargs)
    pod_list = k8s_pods.get_pods_by_deployment(deployment)
    pod_map = {pod.metadata.name: pod for pod in pod_list.items}

    res_stats = DeploymentResourceStats(dname)
    for pod in resource['items']:
        pod_name = pod['metadata']['name']
        if 'app' not in pod['metadata']['labels'] and 'run' not in pod['metadata']['labels']:
            continue
        usage_object = get_resource_usage_object_by_pod(pod_name, namespace)
        usage = get_container_usage(usage_object['containers'])
        pod_containers = pod_map[pod_name].spec.containers
        limits = get_container_usage(pod_containers)
        res_stats.add_metric_from_containers(pod_name, limits, usage)

    return res_stats


def get_container_limit(containers):
    memory = 0
    cpu = 0
    for c in containers:
        if 'istio-proxy' in c.name:
            continue
        limits = c.resources.limits
        if limits is None:
            continue
        if 'cpu' in limits:
            cpu += quantity.parse_quantity(limits['cpu'])
        else:
            cpu += 0

        if 'memory' in limits:
            memory += quantity.parse_quantity(limits['memory'])
        else:
            memory += 0
        return dict(cpu = cpu, memory = memory)

def get_container_usage(containers):
    memory = 0
    cpu = 0
    if isinstance(containers, list) and isinstance(containers[0], dict):
        assert len(containers) <= 2, "Only 2 containers allowed"
        for c in containers:
            cpu += quantity.parse_quantity(c['usage']['cpu'])
            memory += quantity.parse_quantity(c['usage']['memory'])
    else:
        for c in containers:
            if 'istio-proxy' in c.name:
                continue
            limits = c.resources.limits
            if limits is None:
                continue
            if 'cpu' in limits:
                cpu += quantity.parse_quantity(limits['cpu'])
            else:
                cpu += 0

            if 'memory' in limits:
                memory += quantity.parse_quantity(limits['memory'])
            else:
                memory += 0
    return dict(cpu = cpu, memory = memory)
