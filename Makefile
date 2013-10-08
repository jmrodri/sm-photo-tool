SRC_DIR := src
PYFILES := `find $(SRC_DIR) -name "*.py"`
# Ignore certdata.py from style checks as tabs and trailing
# whitespace are required for testing.
TESTFILES=`find  test/ \( ! -name certdata.py ! -name manifestdata.py \) -name "*.py"`
STYLEFILES=$(PYFILES) $(TESTFILES)

# we never "remake" this makefile, so add a target so
# # we stop searching for implicit rules on how to remake it
Makefile: ;

pylint:
	@PYTHONPATH="src/:/usr/share/sm-photo-tool" pylint --rcfile=pylintrc $(STYLEFILES)

tablint:
	@! GREP_COLOR='7;31' grep --color -nP "^\W*\t" $(STYLEFILES)

trailinglint:
	@! GREP_COLOR='7;31'  grep --color -nP "[ \t]$$" $(STYLEFILES)

.PHONY: whitespacelint
whitespacelint: tablint trailinglint

#INDENT_IGNORE = "E121,E122,E123,E124,E125,E126,E127,E128"
pep8:
	@TMPFILE=`mktemp` || exit 1; \
	pep8 --ignore E501,$(INDENT_IGNORE) --exclude ".#*" --repeat src $(STYLEFILES) | tee $$TMPFILE; \
	! test -s $$TMPFILE

.PHONY: stylish
stylish: whitespacelint pep8
