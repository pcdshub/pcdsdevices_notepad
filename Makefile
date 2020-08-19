beamlines := cxi xcs xpp mec mfx hxd icl kfe lfe mec mfx pbt tmo
configs   := ${beamlines:=.json}

all: $(configs)

%.json:
	python notepad_finder.py --file $@ beamline=$(basename $@)

pvs:
	for fn in $(configs); do \
		json_pp < $$fn | \
			grep -e read_pv -e write_pv | \
			grep -v -e null; \
	done

.PHONY: all pvs
