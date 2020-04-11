build:
	docker build . -t health_api:latest

stop:
	docker stop $$(docker ps -a |grep health_api | awk '{print $$1}')

rm:
	docker rm $$(docker ps -a |grep health_api | awk '{print $$1}')

forcebuild:
	docker build --no-cache . -t health_api:latest

run:
	docker run -d -p 8000:8000 health_api:latest

localrun:
	FLASK_APP=main.py flask run --port 8000 --host=0.0.0.0

forceall: stop rm forcebuild run

all: forcebuild run