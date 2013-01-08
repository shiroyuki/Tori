package:
	python setup.py sdist

doc: clean
	cd docs && make clean && make html

doc_update:
	cd docs && make html

test: clean
	cd test && python test.py
	cd test && python3 test.py

clean:
	rm -Rf MANIFEST dist docs/build/*
	find . -name .DS_Store -exec rm {} \;
	find . -name ._* -exec rm {} \;
	find . -name *.pyc -exec rm {} \;