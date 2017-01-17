DOC=docs
TEST=tests

#all: init doc test
all: doc test

init:
	pip3 install -r requirements.txt

test:
	cd $(TEST) && $(MAKE)

doc:
	cd $(DOC) && $(MAKE)
