.PHONY: all fonts web zip preview screenshots test release clean

PYTHON ?= python3

all: release

fonts:
	$(PYTHON) src/build_font.py

release:
	$(PYTHON) src/build_release.py

web: fonts
	$(PYTHON) src/build_release.py --skip-tests --skip-screenshots

zip: release

preview:
	$(PYTHON) src/make_preview.py

screenshots:
	$(PYTHON) src/make_screenshots.py

test:
	$(PYTHON) tests/test_font.py

clean:
	rm -f dist/MITMediaLabFont-*.ttf dist/MITMediaLabFont-*.otf dist/MITMediaLabFont.zip
	rm -f dist/preview-glyphs.png
