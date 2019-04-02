# Tartiflette-aiohttp Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Release]

### [0.6.0] - 2019-04-02

#### Changed

- Accept `tartiflette` version between >=0.6.5 and <0.8.0.

### [0.5.1] - 2019-03-29

#### Fixed

- Pass the "operation name" to the execution _(engine)_.

### [0.5.0] - 2019-03-25

#### Changed

- An unique reference of the `executor_context` is passed for each request. Thanks to a shallow copy.

### [0.4.2] - 2019-03-06

#### Changed

- Improve subscription error handling by using `send_error` method instead of `send_message`.

### [0.4.1] - 2019-03-05

#### Fixed

- [ISSUE-10](https://github.com/dailymotion/tartiflette-aiohttp/issues/10): Now handle errors in the subscription generator, send an error message to the client and finish the _on_start method.

### [0.4.0] - 2019-03-04

#### Changed

- Move Tartiflette deps to 0.6.x branch. See [here](https://github.com/dailymotion/tartiflette/blob/master/CHANGELOG.md) for more details

### [0.3.1] - 2019-02-28

#### Fix

- Fix WebSockets handler to works even if `executor_http_methods` allows only `POST` method.

### [0.3.0] - 2019-02-25

- Add a built-in handler for WebSocket subscriptions.

### [0.2.1] - 2019-02-21

- Add an optional GraphiQL view handler.

### [0.2.0] - 2019-01-14

- Update Tartiflette deps to 0.3.x

### [0.1.2] - 2018-12-07

#### Added

- Add code that implements interface describe in the README.md file.

### [0.1.1] - 2018-12-06

#### Added

- Everythings needed to have a package and a little CI.

## [Unreleased]

### [0.1.0] - 2018-12-05

#### Added

- README.md & LICENSE
