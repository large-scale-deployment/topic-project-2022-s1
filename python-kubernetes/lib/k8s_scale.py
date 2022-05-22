from kubernetes import client

def scale_up_deployment(deployment, by_replica=1):
    name, namespace = deployment.metadata.name, deployment.metadata.namespace
    apiAppsV1 = client.AppsV1Api()
    scale = apiAppsV1.read_namespaced_deployment_scale(name, namespace)
    new_replicas = scale.spec.replicas + by_replica
    scale.spec.replicas = new_replicas
    apiAppsV1.patch_namespaced_deployment_scale(name, namespace, body=scale.to_dict())
    scale = apiAppsV1.read_namespaced_deployment_scale(name, namespace)

    return new_replicas == scale.spec.replicas

