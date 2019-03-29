
.PHONY: init
init:
	true

.PHONY: format
format:
	black -l 79 --py36 tartiflette_aiohttp setup.py

.PHONY: check-format
check-format:
	black -l 79 --py36 --check tartiflette_aiohttp setup.py

.PHONY: style
style: check-format
	pylint tartiflette_aiohttp --rcfile=pylintrc

.PHONY: complexity
complexity:
	xenon --max-absolute B --max-modules B --max-average A tartiflette_aiohttp

.PHONY: test-integration
test-integration: clean
	py.test -s tests/integration --junitxml=reports/report_integ_tests.xml --cov . --cov-config .coveragerc --cov-report term-missing --cov-report xml:reports/coverage_integ.xml

.PHONY: test-unit
test-unit: clean
	mkdir -p reports
	py.test -s tests/unit --junitxml=reports/report_unit_tests.xml --cov . --cov-config .coveragerc --cov-report term-missing --cov-report xml:reports/coverage_func.xml

.PHONY: test-functional
test-functional: clean
	mkdir -p reports
	py.test -s tests/functional --junitxml=reports/report_func_tests.xml --cov . --cov-config .coveragerc --cov-report term-missing --cov-report xml:reports/coverage_unit.xml

.PHONY: test
test: test-integration test-unit test-functional

.PHONY: clean
clean:
	find . -name '*.pyc' -exec rm -fv {} +
	find . -name '*.pyo' -exec rm -fv {} +
	find . -name '__pycache__' -exec rm -frv {} +
