package:
	python setup.py sdist

doc: clean
	cd docs && make clean && make html

doc_update:
	cd docs && make html

test: clean
	nosetests -c nose.cfg
	nosetests-3.3 -c nose.cfg

install:
	sudo python setup.py install --optimize 2 --compile

clean:
	rm -Rf MANIFEST dist docs/build/*
	find . -name .DS_Store -exec rm {} \;
	find . -name ._* -exec rm {} \;
	find . -name *.pyc -exec rm {} \;