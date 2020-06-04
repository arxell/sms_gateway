SRC := src

# PROTO
compile-sms-proto:
	python3 -m grpc_tools.protoc \
		-I proto/ \
		--python_out=$(SRC)/app/protos/sms/ \
		--python_grpc_out=$(SRC)/app/protos/sms/ \
		--grpc_python_out=$(SRC)/app/protos/sms/ \
		proto/sms.proto

	# why sed? Because https://github.com/protocolbuffers/protobuf/issues/1491
	sed -i -E 's/^\(import.*_pb2\)/from . \1/' $(SRC)/app/protos/sms/*.py
	# clean after sed
	rm $(SRC)/app/protos/sms/*py-E

compile-proto: compile-sms-proto

# REQUIREMENTS
install-pip:
	pip install poetry==1.0.5

compile-requirements: install-pip
	# update poetry.lock
	poetry lock
	# update requirements/requirements.txt
	poetry export --without-hashes -f requirements.txt -o requirements/requirements.txt
	# requirements/requirements_dev.txt
	poetry export --dev --without-hashes -f requirements.txt -o requirements/requirements_dev.txt

sync-requirements: install-pip
	# install in a current virtualenv packages from poetry.lock
	poetry install

show-outdated-requirements: install-requirements
	poetry update --dry-run | grep Updating | sed s/Updating/Outdated/g

update-requirements: install-pip
	# update poetry.lock
	poetry update --lock

requirements: update-requirements compile-requirements sync-requirements


# CODE: CHECKS
check-isort:
	./code_checks/make_isort.sh $(SRC)

check-black:
	./code_checks/make_black.sh $(SRC)

check-autoflake:
	./code_checks/make_autoflake.sh $(SRC)

check-format: check-autoflake check-black check-isort

check-mypy:
	rm -rf .mypy_cache
	PYTHONPATH="$(SRC)" \
		mypy --config-file=setup.cfg $(SRC)

check-helm:
	helm lint .cicd/deploy/k8s/gg-subscription-service


# CODE: FORMAT
isort:
	./code_checks/make_isort.sh -f $(SRC)

black:
	./code_checks/make_black.sh -f $(SRC)

autoflake:
	./code_checks/make_autoflake.sh -f $(SRC)

format: autoflake black isort

# TESTS
tests:
	cd $(SRC) && pytest . -s -v --cov app/ --cov-report term-missing --cov-config=../setup.cfg

check: format tests

# RUN
run-server:
	cd $(SRC) && python main.py run-server

check-server:
	cd $(SRC) && python main.py check-server

send-sms:
	cd $(SRC) && python main.py send-sms

run-deps:
	docker-compose -f docker-compose.yml up -d --build kafka zookeeper

