from kubernetes import client, config

def block_ips(ips):
    apiCustObject = client.CustomObjectsApi() # Patch authorisation policy
    params = dict(
            group ='security.istio.io',
            version = 'v1beta1',
            namespace = 'istio-system',
            plural='authorizationpolicies',
            name = "ingress-policy")
    block_ips_policy = apiCustObject.get_namespaced_custom_object(**params)
    ip_list = block_ips_policy['spec']['rules'][0]['from'][0]['source']['remoteIpBlocks']
    for ip in ips:
        tmp = ip.strip()
        if tmp not in ip_list:
            ip_list.append(tmp)

    patch_params = dict(body = block_ips_policy, **params)
    apiCustObject.patch_namespaced_custom_object(**patch_params)
    block_ips_policy = apiCustObject.get_namespaced_custom_object(**params)

    ip_list_new = block_ips_policy['spec']['rules'][0]['from'][0]['source']['remoteIpBlocks']
    return ip_list_new == ip_list

if __name__ == '__main__':
    config.load_kube_config()
    print('ok')
    result = block_ips(['192.168.1.11', '192.168.1.22'])
    print(result)
