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

deploy-k8s:
	kubectl apply -f autoscaler-test.yaml
	kubectl expose deployment/autoscaler-test --type="NodePort" --port 1323

K8S_SVC_NAME=autoscaler-test
service-info:
	@$(eval NODE_PORT=$(shell kubectl get services/$(K8S_SVC_NAME) -o go-template='{{(index .spec.ports 0).nodePort}}'))
	@echo URL: http://localhost:$(NODE_PORT)/alloc_memory?mbs=10

