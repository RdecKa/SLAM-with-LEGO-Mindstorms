SHELL=/bin/bash
VENV_NAME=.venv
PYTHON=${VENV_NAME}/bin/python3
PIP=${VENV_NAME}/bin/pip3

requirements:
	${PIP} install -r requirements.txt

init:
	python3.8 -m venv .venv
	make requirements
	cp slam/config.py.sample slam/config.py
	cp slam/mindstorms/slam_lego/config.py.sample slam/mindstorms/slam_lego/config.py

run:
	${PYTHON} -m slam

runlego:
	${PYTHON} -m slam lego

test:
	# Run tests in folder ./tests
	${PYTHON} -m unittest discover -s tests
