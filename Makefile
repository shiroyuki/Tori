TEST_FLAGS=""

package:
	python setup.py sdist

doc: clean
	cd docs && make clean && make html

doc_update:
	cd docs && make html

test: test_py3

test_py2: cache_clean# reset_mongodb
	nosetests -c nose.cfg $(TEST_FLAGS)

test_py3: cache_clean# reset_mongodb
	nosetests-3.3 -c nose.cfg $(TEST_FLAGS)

test_ci: cache_clean install_test_package reset_mongodb
	nosetests -c nose.cfg ut
	nosetests -c nose.cfg ut/db
	nosetests -c nose.cfg ft
	nosetests -c nose.cfg ft/db
	#nosetests -c nose.cfg

install_test_package:
	python setup_for_test_only.py install --optimize 2 --compile

reset_mongodb:
	# New
	mongo t3test --eval 'db.dropDatabase()' > /dev/null
	# Deprecated
	mongo test_tori_db_manager --eval 'db.dropDatabase()' > /dev/null
	mongo test_tori_db_mapper_link --eval 'db.dropDatabase()' > /dev/null
	mongo test_tori_db_session --eval 'db.dropDatabase()' > /dev/null
	mongo test_tori_db_session_assoc_m2m --eval 'db.dropDatabase()' > /dev/null
	mongo test_tori_db_uow_cascade_on_refresh --eval 'db.dropDatabase()' > /dev/null

install:
	python setup.py install --optimize 2 --compile

cache_clean:
	find . -name *.pyc -exec rm {} \;

clean: cache_clean
	rm -Rf MANIFEST dist docs/build/*
	find . -name __pycache__ -exec rm -Rf {} \;
	find . -name .DS_Store -exec rm {} \;
	find . -name ._* -exec rm {} \;
