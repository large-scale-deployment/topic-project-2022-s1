from datetime import datetime
from elasticsearch import Elasticsearch
client = Elasticsearch()
query = {
    'bool': {
        'must':{'match': {'response_code':403}},
        'filter':{
            'range': {
                'start_time': {
                    'gte': '2022-05-15'
                }
            }
        }
    }
}
response = client.search(
    index="envoy-k8s",
    query=query,
    sort={"start_time": {"order": "desc"}},
    size = 1000
)
ips = {}
for hit in response['hits']['hits']:
  source = hit['_source']
  x_forwarded_for = source['x_forwarded_for']
  if source['response_code'] == '403':
    count = ips.get(x_forwarded_for, 0)
    count = count + 1
    ips[x_forwarded_for] = count

print(f"total: {response['hits']['total']['value']}")
for ips, count in ips.items():
  print(f"{ips}: {count}")
  if count >= 3:
      ip_list = ips.split(',')
      block_ips('ingress-policy', ip_list)

# curl -v -s -H 'X-Forwarded-For: 56.5.6.7, 72.9.5.6, 98.1.2.3' "$GATEWAY_URL"/get?show_env=true
