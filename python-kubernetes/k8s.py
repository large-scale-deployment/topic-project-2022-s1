from kubernetes import client, config
import json
from datetime import datetime

def format_datetime(dt: datetime):
  return dt.strftime('%Y-%m-%dT%H:%M:%S%Z')

def to_datetime(s: str):
  return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%Z')


# Blah blah

# Return seconds
# t2 - t1
def diff_datetime(t1: str, t2: str):
  ta = to_datetime(t1)
  tb = to_datetime(t2)
  return (tb - ta).seconds

class K8SStats:
  def __init__(self) -> None:
    self._v1 = client.CoreV1Api()
    self._image_sizes = {}
  
  def get_image_sizes(self):
    return self._image_sizes

  def collect_image_size(self):
    self._image_sizes = {}
    for node in self._v1.list_node().items:
      for image in node.status.images:
        for n in image.names:
          self._image_sizes[n] = image.size_bytes

  def collect_pods_status(self, namespace):
    ret = self._v1.list_namespaced_pod(namespace)
    pods = []
    for i in ret.items:
      conditions = {}
      for cond in i.status.conditions:
        conditions[cond.type] = {
          'last_probe_time': cond.last_probe_time,
          'status': bool(cond.status),
          'last_transition_time': format_datetime(cond.last_transition_time)
        }
      image_name = i.status.container_statuses[-1].image
      pods.append({
        'name': i.metadata.name,
        'namespace': i.metadata.namespace,
        'container_statuses': {
          'image': i.status.container_statuses[-1].image,
          'image_size': self._image_sizes[image_name],
          'id': i.status.container_statuses[-1].image_id,
          'name': i.status.container_statuses[-1].name,
          'ready': i.status.container_statuses[-1].ready,
          'started': i.status.container_statuses[-1].started,
          'restart_count': i.status.container_statuses[-1].restart_count,
          'running_at': format_datetime(i.status.container_statuses[-1].state.running.started_at),
        },
        'phase': i.status.phase,
        'conditions': conditions,
        'start_time': format_datetime(i.status.start_time),
      })
    return pods

  def collect_pods_start_time(self, namespace='default'):
    # Pod conditions:
    # 1. PodScheduled the Pod has been scheduled to a node.
    # 2. ContainersReady all containers in the Pod are ready.
    # 3. Initialized all init containers have completed successfully.
    # 4. Ready the Pod is able to serve requests and should be added to the load balancing pools of all matching Services.
    # Return the time between every two stages
    pods_status = self.collect_pods_status(namespace)

    start_times = []
    for ps in pods_status:
      name = ps["name"]
      conditions = ps['conditions']
      t1 = conditions['PodScheduled']['last_transition_time']
      t2 = conditions['Initialized']['last_transition_time']
      
      p_c = diff_datetime(t1, t2)

      t1 = conditions['Initialized']['last_transition_time']
      t2 = conditions['ContainersReady']['last_transition_time']
      i_c = diff_datetime(t1, t2)

      t1 = conditions['ContainersReady']['last_transition_time']
      t2 = conditions['Ready']['last_transition_time']
      c_r = diff_datetime(t1, t2)

      t1 = conditions['PodScheduled']['last_transition_time']
      t2 = conditions['Ready']['last_transition_time']
      p_r = diff_datetime(t1, t2)
      start_times.append(dict(
        name = name, p_c = p_c, i_c = i_c, c_r = c_r, p_r = p_r,
        pod_scheduled = conditions['PodScheduled']['last_transition_time'],
        initialized = conditions['Initialized']['last_transition_time'],
        containers_ready = conditions['ContainersReady']['last_transition_time'],
        ready = conditions['Ready']['last_transition_time'],
      ))
    return start_times

if __name__ == "__main__":
  config.load_kube_config()
  stats = K8SStats()
  stats.collect_image_size()
  print(stats.get_image_sizes())
  sorted = sorted(stats.collect_pods_start_time(), key= lambda x: x['ready'])
  print(json.dumps(stats.collect_pods_start_time()))
  print(json.dumps(sorted))
