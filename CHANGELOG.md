# CHANGELOG

<!-- version list -->

## v1.3.0 (2026-04-17)

### Code Style

- Make the `disclose` function output stuff in actual proper python format
  ([`1c18157`](https://github.com/nachollorca/lmra/commit/1c181576878ad600cbb5b077ec50af5a3a510af5))

### Documentation

- Add comment for the tool.fn explanation and remove unused import
  ([`59537b6`](https://github.com/nachollorca/lmra/commit/59537b6534116e1a2c21c86c774f2fce1744978d))

- Fix how the references look in readme
  ([`23e7060`](https://github.com/nachollorca/lmra/commit/23e706021756bf523713f559b194e1094f4c4d85))

- Make readme cool
  ([`d765cf5`](https://github.com/nachollorca/lmra/commit/d765cf55e8ee38c589ba9e1e3f73ac468aa98566))

### Features

- Add tools to the demo
  ([`e288158`](https://github.com/nachollorca/lmra/commit/e288158928cf40aa26ed69c9cd615a920224cbbc))


## v1.2.0 (2026-04-16)

### Continuous Integration

- Fix a typing problem
  ([`e2a2f9a`](https://github.com/nachollorca/lmra/commit/e2a2f9a7239d9733d555837b6446e4a2a3ccccee))

### Documentation

- Add preliminary readme
  ([`1adb260`](https://github.com/nachollorca/lmra/commit/1adb2609441b08b4d3bb56e2eaf4771e8f5596a3))

- Reduce some verbosity in docstrings
  ([`aafb474`](https://github.com/nachollorca/lmra/commit/aafb47406e5f29dd5650febf7aeb9f8a095e4511))

### Features

- Add streamlit gui
  ([`afa136b`](https://github.com/nachollorca/lmra/commit/afa136b50e802ffe2001b11b0d7b79f8fb230d8b))

- First tool / progressive disclosure iteration
  ([`d7f8b1f`](https://github.com/nachollorca/lmra/commit/d7f8b1f1dda4736114fa39ddce944ca03da633da))

### Refactoring

- Remove `__shown__` flag from tables because it added unnecessary complexity
  ([`c88e522`](https://github.com/nachollorca/lmra/commit/c88e52211bfed0e27cccf8b44c77807d25fcf4fa))

### Testing

- Improve the test printing
  ([`9160d26`](https://github.com/nachollorca/lmra/commit/9160d26a42aea980f771e8d51ecba75279716e46))

- Remove extra main from tested script
  ([`4246dd1`](https://github.com/nachollorca/lmra/commit/4246dd12378235fd0f259ff3c65da2faa0875f48))


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
