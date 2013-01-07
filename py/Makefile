# Copyright Philip Bergen 2012, all rights reserved

# If it prints directory names invoke with --no-print-directory
#   alias make='make --no-print-directory'

# Default shell is not bash
SHELL := /bin/bash
# No default suffix rules
.SUFFIXES: 

# Hidden directory to store marker files in
TMP = .tmp
TMPD = $(TMP)/.hold

TEST_MDFILES = $(addsuffix .test,$(addprefix $(TMP)/,$(wildcard *.md)))
TEST_PYFILES = $(addsuffix .test,$(addprefix $(TMP)/,$(wildcard *.py)))

all:: test

$(TMPD):
	@mkdir -p $(TMP)
	@touch $@

$(TMP)/%.md.test: %.md $(TMPD) simcpu.py
	@echo TEST $<
	@echo -e "import doctest\ndoctest.testfile('$<')" | python && echo "OK" > $@

$(TMP)/%.py.test: %.py $(TMPD) simcpu.py
	@echo TEST $<
	@python -m doctest $< && echo "OK" > $@

test:: $(TEST_MDFILES) $(TEST_PYFILES)

clean::
	rm -fr $(TMP)
	rm -f *.pyo *.pyc

.PHONY: all clean test
