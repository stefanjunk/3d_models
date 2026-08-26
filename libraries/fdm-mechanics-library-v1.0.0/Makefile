.PHONY: sources build previews validate package catalog clean
sources:
	python3 tools/generate_sources.py
build:
	python3 tools/build_library.py --workers 3
previews:
	python3 tools/build_contact_sheets.py
validate:
	python3 tools/validate_library.py
package:
	python3 tools/build_package_manifest.py
catalog:
	python3 tools/query_catalog.py --limit 156
clean:
	find samples -name 'print_plate.stl' -delete
	find samples -name 'preview.png' -delete
	find samples -path '*/parts/part_*.stl' -delete
