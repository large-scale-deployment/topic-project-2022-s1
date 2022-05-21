if __name__ == '__main__':
    from kubernetes import config
    from lib import k8s_deployments, k8s_metrics
    config.load_kube_config()

    deployment = k8s_deployments.get_deployment_by_name('php-apache')
    print(k8s_metrics.get_resource_usage_by_deployment(deployment))


