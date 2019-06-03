from setuptools import find_packages, setup

_TEST_REQUIRE = [
    "pytest==4.4.0",
    "pytest-cov==2.6.1",
    "pytest-asyncio==0.10.0",
    "asynctest==0.13.0",
    "pytz",
    "pylint==2.3.0",
    "xenon==0.5.5",
    "black==18.9b0",
    "isort==4.3.4",
]

_VERSION = "0.7.0"

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
    install_requires=["aiohttp~=3.4", "tartiflette<0.11.0,>=0.10.0"],
    tests_require=_TEST_REQUIRE,
    extras_require={"test": _TEST_REQUIRE},
    include_package_data=True,
)
