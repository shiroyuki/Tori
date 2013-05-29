package:
	python setup.py sdist

doc: clean
	cd docs && make clean && make html

doc_update:
	cd docs && make html

test: cache_clean
	nosetests -c nose.cfg
	nosetests-3.3 -c nose.cfg

test_local: cache_clean
	nosetests -c local.cfg
	nosetests-3.3 -c local.cfg

reset_mongodb:
	mongo test_tori_db_manager --eval 'db.dropDatabase()'
	mongo test_tori_db_mapper_link --eval 'db.dropDatabase()'
	mongo test_tori_db_session --eval 'db.dropDatabase()'
	mongo test_tori_db_session_assoc_m2m --eval 'db.dropDatabase()'
	mongo test_tori_db_uow_cascade_on_refresh --eval 'db.dropDatabase()'

install:
	python setup.py install --optimize 2 --compile

cache_clean:
	find . -name *.pyc -exec rm {} \;

clean: cache_clean
	rm -Rf MANIFEST dist docs/build/*
	find . -name .DS_Store -exec rm {} \;
	find . -name ._* -exec rm {} \;