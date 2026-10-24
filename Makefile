PY ?= python
export PYTHONIOENCODING := utf-8

.PHONY: readme site book book-pdf book-check test-static test-browser verify stats clean

readme:
	$(PY) scripts/build_readme.py

site:
	$(PY) scripts/build_site.py --build

book:
	$(PY) analog-book/build_book.py

book-pdf:
	$(PY) analog-book/build_book.py --pdf

book-check:
	$(PY) analog-book/build_book.py --check --no-build

test-static:
	$(PY) -B -m unittest discover -s scripts -p "test_svg_assets.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_readme_links.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_a11y.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_docs_sync.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_docs_links.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_split_readme.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_page_structure.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_release_gate.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_publish_book.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_site_build.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_smartsymbols.py" -v
	$(PY) -B -m unittest discover -s analog-book/tests -p "test_build.py" -v

test-browser:
	$(PY) -B -m unittest discover -s scripts -p "test_reading_journey.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_diagnostic.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_gallery_interactions.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_learning_interactions.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_waveform_timing.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_svg_layout.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_svg_contrast.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_reduced_motion.py" -v
	$(PY) -B -m unittest discover -s scripts -p "test_first_screen.py" -v
	$(PY) -B -m unittest discover -s analog-book/tests -p "test_browser_book.py" -v

verify: test-static
	$(PY) scripts/build_readme.py --check
	$(PY) analog-book/build_book.py
	$(PY) analog-book/build_book.py --check --no-build

stats:
	$(PY) scripts/build_stats.py

clean:
	$(PY) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in (pathlib.Path('build'), pathlib.Path('analog-book/dist'))]"
	$(PY) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in list(pathlib.Path('.').rglob('__pycache__'))]"
