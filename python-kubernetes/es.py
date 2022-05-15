from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()

import pdb;pdb.set_trace()
resp = es.search(index="envoy-k8s", query={"match_all": {}}, sort='start_time')
#print(resp)
print("Got %d Hits:" % resp['hits']['total']['value'])
for hit in resp['hits']['hits']:
    print("%(start_time)s %(response_code)s: %(x_forwarded_for)s" % hit["_source"])


# curl -v -s -H 'X-Forwarded-For: 56.5.6.7, 72.9.5.6, 98.1.2.3' "$GATEWAY_URL"/get?show_env=true