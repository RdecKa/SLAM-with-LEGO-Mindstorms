SHELL=/bin/bash
VENV_NAME=.venv
PYTHON=${VENV_NAME}/bin/python3
PIP=${VENV_NAME}/bin/pip3

requirements:
	${PIP} install -r requirements.txt

init:
	${PYTHON} -m venv .venv
	make requirements

run:
	${PYTHON} -m slam

test:
	# Run tests in folder ./tests
	${PYTHON} -m unittest discover -s tests
