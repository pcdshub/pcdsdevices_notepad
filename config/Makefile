beamlines            := cxi xcs xpp mec mfx hxd icl kfe lfe tmo
finder_results       := $(addprefix finder/,${beamlines:=.json})
macro_files          := $(addprefix macros/,${beamlines:=.macros.json})
notepad_config_files := $(addprefix notepad/ioc-,$(beamlines:=-pcdsdevices.cfg))
archive_files        := $(addprefix caproto/,$(beamlines:=.notepad.archive))
epicsarch_files      := $(addprefix caproto/,$(beamlines:=_pcdsdevices_notepad.epicsArch.txt))

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

caproto/%.notepad.archive: finder/%.json
	python create_archive_file.py --output $@ $<

caproto/%_pcdsdevices_notepad.epicsArch.txt: finder/%.json
	python create_recorder_file.py --output $@ $<

macros/%.macros.json:
	beamline=$*; \
	if [ ! -f "$@" ]; then \
		echo "Building default macros for beamline: $${beamline}"; \
		echo "{\"engineer_name\":\"engineer\",\"engineer_username\":\"engineer\",\"location\":\"SLAC:LCLS:$${beamline}\",\"iocname\":\"ioc-$${beamline}-pcdsdevices\",\"hutch\":\"$${beamline}\"}" > $@; \
	fi

pvs:
	for fn in $(configs); do \
		json_pp < $$fn | \
			grep -e read_pv -e write_pv | \
			grep -v -e null; \
	done

clean:
	rm -f finder/*.json


.PHONY: all pvs clean
