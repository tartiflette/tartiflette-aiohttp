from setuptools import find_packages, setup


_TEST_REQUIRE = [
    "pytest",
    "pytest-cov",
    "pytest-asyncio",
    "asynctest",
    "pytz",
    "pylint==2.3.1",
    "xenon",
    "black==19.3b0",
]

_VERSION = "0.6.1"

_PACKAGES = find_packages(exclude=["tests*"])

setup(
    name="tartiflette-aiohttp",
    version=_VERSION,
    description="Runs a Tartiflette GraphQL Engine through aiohttp",
    long_description=open("README.md").read(),
    url="https://github.com/dailymotion/tartiflette-aiohttp",
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
    install_requires=["aiohttp~=3.4", "tartiflette<0.8.0,>=0.6.5,!=0.7.0"],
    tests_require=_TEST_REQUIRE,
    extras_require={"test": _TEST_REQUIRE},
    include_package_data=True,
)
