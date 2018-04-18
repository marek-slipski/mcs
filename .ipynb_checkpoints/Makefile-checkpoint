# Makefile Reference:
# target: dependencies
#   rule
# $@ refers to the target of the current rule
# $^ refers to the dependencies of the current rule
# $< refers to the first dependency of the current rule.
# $* refers to matching sets of files in action
# % is a wildcard placeholder in targets and dependencies
# $(VAR) Reference variable VAR
# Use 'wildcard 'function to get lists of files matching a pattern.
# Use 'patsubst' function to rewrite file names.

#Define variables

## download	  :   Download MCS data
.PHONY: download
download: src/download_files.py
	python $<


# clean      :  Remove files
#.PHONY: clean
#clean:
#	rm

.PHONY : help
help : Makefile
	@sed -n 's/^##//p' $<
