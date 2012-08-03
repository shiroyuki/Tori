package:
	python setup.py sdist

clean:
	rm -Rf MANIFEST dist docs/build/*
	find . -name .DS_Store -exec rm -v {} \;
	find . -name ._* -exec rm -v {} \;
	find . -name *.pyc -exec rm -v {} \;