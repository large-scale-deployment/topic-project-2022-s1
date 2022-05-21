from kubernetes import client

def get_deployment_by_name(name, namespace='default'):
    apiAppsV1 = client.AppsV1Api()
    deployment = apiAppsV1.read_namespaced_deployment(name, namespace)
    return deployment

def get_namespaced_deployments(namespace='default'):
    apiAppsV1 = client.AppsV1Api()
    deployments = apiAppsV1.list_namespaced_deployment(namespace)
    return deployments

if __name__ == "__main__":
    import json
    from kubernetes import config
    config.load_kube_config()
    deployment = get_deployment_by_name('httpbin')
    # print(deployment.to_dict())
    for d in get_namespaced_deployments('default').items:
        print(d.metadata.name)
