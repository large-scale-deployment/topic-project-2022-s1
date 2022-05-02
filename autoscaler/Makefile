K8S_SVC_NAME=autoscaler-test

all: build deploy-k8s service-info
 
clean-k8s:
	@-kubectl delete service -l app=autoscaler-test
	@-kubectl delete deployment -l app=autoscaler-test
	@echo Waiting for a while while the deployment is being deleted
	@sleep 2

clean-docker: clean-k8s
	@-docker image rm wxwmatt/autoscaler-test:1.0

clean: clean-docker

build: clean
	docker build -t wxwmatt/autoscaler-test:1.0 .

gen-deployment:
	kubectl create deployment autoscaler-test --image=wxwmatt/autoscaler-test:1.0 --dry-run=client -o=yaml \
		> autoscaler-test.yaml

run-container:
	docker run --rm -it -p 1323:1323 wxwmatt/autoscaler-test:1.0

deploy-k8s:
	kubectl apply -f autoscaler-test.yaml
	kubectl expose deployment/autoscaler-test --type="NodePort" --port 1323

service-info:
	@$(eval NODE_PORT=$(shell kubectl get services/$(K8S_SVC_NAME) -o go-template='{{(index .spec.ports 0).nodePort}}'))
	@echo URL: http://localhost:$(NODE_PORT)/alloc_memory?mbs=10

autoscale:
	kubectl autoscale deployment $(K8S_SVC_NAME) --cpu-percent=50 --min=1 --max=5
