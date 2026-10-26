PY ?= python
export PYTHONIOENCODING := utf-8

.PHONY: readme gen bookdata labs fonts site book book-pdf book-check test-static test-browser verify stats clean

readme:
	$(PY) scripts/build_readme.py

# docs/ 是唯一内容源，下面四样产物都从它派生；改完 docs/ 必须一起重生，
# 否则 CI 里的对账测试（README、实验包 zip、字体子集缺字、animations.yml）必然红灯。
# fonts 需要源字体：首次先跑 `python scripts/subset_fonts.py --download`（要联网）。
gen: readme bookdata labs fonts

bookdata:
	$(PY) scripts/build_book_data.py --write

labs:
	$(PY) scripts/build_lab_packages.py

fonts:
	$(PY) scripts/subset_fonts.py --build

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
	$(PY) -B -m unittest discover -s scripts -p "test_publish_a4_book.py" -v
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
	$(PY) scripts/build_book_data.py --check
	$(PY) scripts/build_lab_packages.py --check
	$(PY) scripts/subset_fonts.py --check
	$(PY) analog-book/build_book.py
	$(PY) analog-book/build_book.py --check --no-build

stats:
	$(PY) scripts/build_stats.py

clean:
	$(PY) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in (pathlib.Path('build'), pathlib.Path('analog-book/dist'))]"
	$(PY) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in list(pathlib.Path('.').rglob('__pycache__'))]"
