from kubernetes import client
def get_pods_by_deployment(deployment):
    # name like `details`
    dname = deployment.metadata.name
    namespace = deployment.metadata.namespace
    # apiCoreV1.list_namespaced_pod(namespace='default', label_selector=f'app=details')
    apiCoreV1 = client.CoreV1Api()
    return apiCoreV1.list_namespaced_pod(namespace=namespace, label_selector=f'app={dname}')

if __name__ == "__main__":
    import k8s_deployments
    import json
    from kubernetes import config
    import utils
    config.load_kube_config()
    deployment = k8s_deployments.get_deployment_by_name('httpbin')
    pods = get_pods_by_deployment(deployment)
    print(json.dumps(utils.sanitize_for_serialization(pods), indent=4))