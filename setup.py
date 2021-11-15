from setuptools import find_packages, setup

_TEST_REQUIRE = [
    "pytest==6.2.5",
    "pytest-cov==3.0.0",
    "pytest-asyncio==0.16.0",
    "pytest-aiohttp==0.3.0",
    "asynctest==0.13.0",
    "pytz",
    "pylint==2.11.1",
    "xenon==0.8.0",
    "black==20.8b1",
    "isort==5.10.1",
    "async_generator==1.10;python_version=='3.6.*'",
]

_VERSION = "1.4.1"

_PACKAGES = find_packages(exclude=["tests*"])

setup(
    name="tartiflette-aiohttp",
    version=_VERSION,
    description="Runs a Tartiflette GraphQL Engine through aiohttp",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tartiflette/tartiflette-aiohttp",
    author="Dailymotion Core API Team",
    author_email="team@tartiflette.io",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords="api graphql protocol api rest relay tartiflette dailymotion",
    packages=_PACKAGES,
    install_requires=[
        "aiohttp>=3.5.4,<3.9.0",
        "async_generator;python_version=='3.6.*'",
        "tartiflette>=0.12.0,<2.0.0",
    ],
    tests_require=_TEST_REQUIRE,
    extras_require={"test": _TEST_REQUIRE},
    include_package_data=True,
)
