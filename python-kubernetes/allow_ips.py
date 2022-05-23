from lib.k8s_istio import allow_ips

if __name__ == '__main__':
    from kubernetes import config
    config.load_kube_config()
    result = allow_ips('ingress-policy',[])
    print(result)
