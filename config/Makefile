beamlines :=  \
	cxi \
	hxd \
	icl \
	kfe \
	lfe \
	mec \
	mfx \
	rix \
	tmo \
	xcs \
	xpp

finder_results       := $(addprefix finder/,${beamlines:=.json})
macro_files          := $(addprefix macros/,${beamlines:=.macros.json})
notepad_config_files := $(addprefix notepad/ioc-,$(beamlines:=-pcdsdevices.cfg))

all: $(finder_results) $(archive_files) $(epicsarch_files) $(notepad_config_files) $(macro_files)

finder/%.json:
	beamline=$*; \
		python notepad_finder.py --output $@ beamline=$${beamline} --update

notepad/ioc-%-pcdsdevices.cfg: finder/%.json macros/%.macros.json pvnotepad_template.cfg
	python create_pvnotepad_configuration.py \
		--output $@ \
		--template=pvnotepad_template.cfg \
		--macro-file=macros/$*.macros.json \
		$<

macros/%.macros.json:
	beamline=$*; \
	if [ ! -f "$@" ]; then \
		echo "Building default macros for beamline: $${beamline}"; \
		echo "{\"engineer_name\":\"engineer\",\"engineer_username\":\"engineer\",\"location\":\"SLAC:LCLS:$${beamline}\",\"iocname\":\"ioc-$${beamline}-pcdsdevices\",\"hutch\":\"$${beamline}\"}" | json_pp > $@; \
	fi

pvs:
	for fn in $(configs); do \
		json_pp < $$fn | \
			grep -e read_pv -e write_pv | \
			grep -v -e null; \
	done

iocs:
	make -C iocs

clean:
	rm -f finder/*.json


.PHONY: all pvs clean iocs
