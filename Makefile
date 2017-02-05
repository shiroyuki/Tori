TEST_FLAGS=""

package:
	# For development only
	python setup.py sdist

release:
	python setup.py sdist upload

wheel_release:
	python setup.py sdist bdist_wheel upload

doc: clean
	cd docs && make clean && make html

doc_update:
	cd docs && make html

test:
	@echo "Test disabled"

clean:
	rm -Rf MANIFEST build dist docs/build/*
	find . -name __pycache__ -exec rm -Rf {} \;
	find . -name .DS_Store -exec rm {} \;
	find . -name ._* -exec rm {} \;
