lint:
	pep8 --ignore=E303,E251,E201,E202 ./txque --max-line-length=140
	find ./txque -name '*.py' | xargs pyflakes

install:
	python setup.py install

apidocs:
	rm -rf docs/source
	sphinx-apidoc -o docs/source coinbits coinbits/**/tests coinbits/tests
