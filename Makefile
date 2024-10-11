# custom targets
.PHONY: environment
# setup python environment
environment:
	pyenv install -s 3.11.9 ;\
	pyenv virtualenv 3.11.9 multiagent-customer-support ;\
	pyenv local multiagent-customer-support

.PHONY: requirements
# install core requirements
requirements:
	pip install --upgrade pip
	pip install pdm
	pdm install