from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()

import pdb;pdb.set_trace()
resp = es.search(index="envoy-k8s", query={"match_all": {}})
print(resp)
print("Got %d Hits:" % resp['hits']['total']['value'])
for hit in resp['hits']['hits']:
    print("%(start_time)s %(response_code)s: %(x_forwarded_for)s" % hit["_source"])
