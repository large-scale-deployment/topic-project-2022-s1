import json
from kubernetes import client
from kubernetes.utils import quantity

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

  def add_metric_from_containers(self, container_limits, container_usages):
    limits = get_container_usage(container_limits)
    usage = get_container_usage(container_usages)
    cpu_usage = usage['cpu'] * 1000
    memory_usage = usage['memory']
    cpu_limit = limits['cpu'] * 1000
    memory_limit = limits['memory']
    self._metrics.append(dict(
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

    if int(cpu) == 0:
      cpu = 0xffffffff
    return cpu

  def memory_limit(self, value=False):
    memory = 0
    for metric in self._metrics:
      memory += metric['memory_limit']

    if int(memory) == 0:
      memory = 0xffffffff
    if value:
      return memory
    else:
      return format_size(memory, binary=True)

  def __repr__(self):
    return f'app: {self._app_name}, cpu_rate: {round(self.cpu_usage()/self.cpu_limit(), 2)}, memory_rate: {round(self.memory_usage(True)/self.memory_limit(True),2)}, cpu_usage: {self.cpu_usage()}, memory_usage: {self.memory_usage()}, cpu_limit: {self.cpu_limit()}, memory_limit: {self.memory_limit()}'

  def __str__(self):
    return self.__repr__()

def list_namespaced_pod_resource_usage(namespace):
    apiCoreV1 = client.CoreV1Api()
    apiCustObject = client.CustomObjectsApi()

    metric_params = dict(group="metrics.k8s.io",version="v1beta1", namespace=namespace, plural="pods")
    resource = apiCustObject.list_namespaced_custom_object(**metric_params)

    usages = {}
    for pod in resource['items']:
      pod_name = pod['metadata']['name']
      if 'app' not in pod['metadata']['labels'] and 'run' not in pod['metadata']['labels']:
        continue
      app_name = pod['metadata']['labels'].get('app', pod['metadata']['labels'].get('run'))

      target_pod = apiCoreV1.read_namespaced_pod(pod_name, namespace='default')
      container_limits = target_pod.spec.containers
      container_usages = pod['containers']
      stats = usages.get(app_name, DeploymentResourceStats(app_name))
      stats.add_metric_from_containers(container_limits, container_usages)
      usages[app_name] = stats

    return usages

if __name__ == '__main__':
    from humanfriendly import format_size
    import json
    from kubernetes import config
    config.load_kube_config()

    print(list_namespaced_pod_resource_usage('default'))
