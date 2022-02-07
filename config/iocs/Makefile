EPICS_GIT ?= /afs/slac/g/cd/swe/git/repos/package/epics/

all:
	@echo "Checking out and updating IOCs..."
	@for fn in ../notepad/*.cfg; do \
		hutch=$$(echo $$fn | sed s/.*ioc-// | sed s/-pcdsdevices.cfg// ); \
		echo "Hutch: $$hutch"; \
		ioc_path=$(EPICS_GIT)/ioc/$$hutch/pvNotepad.git; \
		echo "Repo: $$ioc_path"; \
		if [ -d $$ioc_path ]; then \
			echo "* Found IOC in AFS git"; \
			git clone $$ioc_path $$hutch; \
			cp $$fn $$hutch; \
			git add $$hutch/$$(basename $$fn); \
			git status $$hutch && git diff $$hutch; \
		else \
			echo "* Not found: $$ioc_path"; \
		fi; \
		echo; \
	done
	@echo Done


.PHONY: all
