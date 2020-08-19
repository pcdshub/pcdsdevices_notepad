beamlines := cxi xcs xpp mec mfx hxd icl kfe lfe mec mfx pbt tmo
configs   := ${beamlines:=.json}
archive_files := ${beamlines:=.notepad.archive}
epicsarch_files := ${beamlines:=_pcdsdevices_notepad.epicsArch.txt}

all: $(configs) $(archive_files) $(epicsarch_files)

%.json:
	python notepad_finder.py --output $@ beamline=$(basename $@)

%.notepad.archive: %.json
	python create_archive_file.py --output $@ $<

%_pcdsdevices_notepad.epicsArch.txt: %.json
	python create_recorder_file.py --output $@ $<

pvs:
	for fn in $(configs); do \
		json_pp < $$fn | \
			grep -e read_pv -e write_pv | \
			grep -v -e null; \
	done

.PHONY: all pvs
