clean:
	kubectl delete deployment -l app=autoscaler-test
	kubectl delete service -l app=autoscaler-test
	docker image rm wxwmatt/autoscaler_test:1.0

build:
	docker build -t wxwmatt/autoscaler_test:1.0 .

gen-deployment:
	kubectl create deployment autoscaler-test --image=wxwmatt/autoscaler_test:1.0 --dry-run=client -o=yaml \
		> autoscaler-test.yaml

all: clean build

