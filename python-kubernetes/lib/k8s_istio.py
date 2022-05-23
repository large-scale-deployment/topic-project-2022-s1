from kubernetes import client

def get_authorizationpolicies(name, namespace='istio-system'):
    apiCustObject = client.CustomObjectsApi() # Patch authorisation policy
    params = dict(
        group ='security.istio.io',
        version = 'v1beta1',
        namespace = namespace,
        plural='authorizationpolicies',
        name = name
    )
    policy = apiCustObject.get_namespaced_custom_object(**params)
    return policy

def patch_authorizationpolicies(policy):
    apiCustObject = client.CustomObjectsApi() # Patch authorisation policy
    name = policy['metadata']['name']
    namespace = policy['metadata']['namespace']

    params = dict(
        group ='security.istio.io',
        version = 'v1beta1',
        namespace = namespace,
        plural='authorizationpolicies',
        name = name
    )

    patch_params = dict(body = policy, **params)
    apiCustObject.patch_namespaced_custom_object(**patch_params)
    # Read after patch
    return apiCustObject.get_namespaced_custom_object(**params)

def block_ips(name, ips, namespace='istio-system'):
    policy = get_authorizationpolicies(name, namespace)
    spec = policy['spec']
    ip_list = spec['rules'][0]['from'][0]['source']['remoteIpBlocks']
    for ip in ips:
        if ip not in ip_list:
            ip_list.append(ip.strip())

    new_policy = patch_authorizationpolicies(policy)

    spec = new_policy['spec']
    ip_list_new = spec['rules'][0]['from'][0]['source']['remoteIpBlocks']
    return ip_list_new

def allow_ips(name, ips, namespace='istio-system'):
    policy = get_authorizationpolicies(name, namespace)
    spec = policy['spec']
    ip_list = spec['rules'][0]['from'][0]['source']['remoteIpBlocks']
    if len(ips) == 0:
        ip_list.clear()
        ip_list.append('127.0.0.127')
    else:
        for ip in ips:
            if ip in ip_list:
                ip_list.remove(ip.strip())

    new_policy = patch_authorizationpolicies(policy)

    spec = new_policy['spec']
    ip_list_new = spec['rules'][0]['from'][0]['source']['remoteIpBlocks']
    return ip_list_new

if __name__ == '__main__':
    from kubernetes import config
    config.load_kube_config()
    print('ok')
    # result =  get_authorizationpolicies('ingress-policy')
    # result = allow_ips('ingress-policy',['98.1.2.3','10.244.1.1'])
    # result = allow_ips('ingress-policy',['72.9.5.6'])
    # result = allow_ips('ingress-policy',[])
    result = block_ips('ingress-policy', ['192.168.1.1'])
    print(result)
