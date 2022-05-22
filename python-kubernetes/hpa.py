if __name__ == '__main__':
    from kubernetes import config
    from lib import k8s_deployments, k8s_metrics, k8s_scale
    import time
    import logging
    logger = logging.getLogger('HPA')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    data_fmt = datefmt='%m-%d %I:%M:%S'
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_fmt, data_fmt)
    ch.setFormatter(formatter)
    logger.addHandler(ch)




    config.load_kube_config()

    while True:
        time.sleep(1)
        deployment = k8s_deployments.get_deployment_by_name('php-apache')
        usage = k8s_metrics.get_resource_usage_by_deployment(deployment)
        if usage.cpu_rate() > 0.8:
            print('Increase replica by 1 and wait for 5 seconds')
            k8s_scale.scale_up_deployment(deployment, 1)
            time.sleep(5)

        logger.info(usage)
