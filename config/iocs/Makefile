EPICS_REPO ?= file:///afs/slac/g/pcds/vol2/svn/pcds

all:
	@echo "Checking out and updating IOCs..."
	@for fn in ../notepad/*.cfg; do \
		hutch=$$(echo $$fn | sed s/.*ioc-// | sed s/-pcdsdevices.cfg// ); \
		echo "Hutch: $$hutch"; \
		ioc_path=$$EPICS_REPO/epics/trunk/ioc/$$hutch/pvNotepad/current; \
		if (svn ls $$ioc_path > /dev/null 2>&1); then \
			echo "* Found IOC in SVN"; \
			svn checkout $$ioc_path $$hutch || svn resolve --accept theirs-full $$hutch; \
			cp $$fn $$hutch; \
			svn add $$hutch/$$(basename $$fn); \
			svn status $$hutch && svn diff $$hutch; \
		else \
			echo "* Not found: $$ioc_path"; \
		fi; \
		echo; \
	done
	@echo Done


.PHONY: all
