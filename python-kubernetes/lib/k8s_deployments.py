from kubernetes import client

def get_deployment_by_name(name, namespace='default'):
    apiAppsV1 = client.AppsV1Api()
    deployment = apiAppsV1.read_namespaced_deployment(name, namespace)
    return deployment

if __name__ == "__main__":
    import json
    from kubernetes import config
    config.load_kube_config()
    deployment = get_deployment_by_name('httpbin')
    import pdb;pdb.set_trace()
    print(json.dumps(deployment.to_dict(), indent=4))
