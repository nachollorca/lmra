# CHANGELOG

<!-- version list -->

## v1.1.0 (2026-04-15)

### Bug Fixes

- Remove the thredingpool timeout because it could not communicate effectively with sqlite
  ([`b891a79`](https://github.com/nachollorca/lmra/commit/b891a797332bded14698bbc92af891128b8fe195))

### Features

- Implement the AST validation
  ([`3c8a21a`](https://github.com/nachollorca/lmra/commit/3c8a21ad4b445ef3ec78b4c4c52bbf77415f118f))

- Include testing demo
  ([`23b0f81`](https://github.com/nachollorca/lmra/commit/23b0f8162916fc3de49a55b07386b00322bc8fb0))

### Performance Improvements

- Make prompt more clear, simple and consistent
  ([`2adced8`](https://github.com/nachollorca/lmra/commit/2adced89a3d6e47d61d770b03c963349c7e690af))

### Refactoring

- Move out of database the utils for context that do not need a session
  ([`7393579`](https://github.com/nachollorca/lmra/commit/73935795b19e7651582bba0281c082cf79fcd01c))

- Use ThreadPoolExecutor for the timeout
  ([`aac50bc`](https://github.com/nachollorca/lmra/commit/aac50bcc1feb5dd9d1b3aedfece4d1ff939c02e4))


## v1.0.0 (2026-04-15)

- Initial Release
