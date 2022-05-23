from lib.k8s_istio import traffic_shifting
if __name__ == '__main__':
  from kubernetes import client, config
  config.load_config()
  new_tf = traffic_shifting('reviews', {'reviews_v1': 50,'reviews_v3': 50 })
  print(new_tf)