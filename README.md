# Example Productizer for IOXIO Dataspace™️

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ioxio-dataspace/example-productizer/blob/main/.pre-commit-config.yaml)
[![image](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Implementation of a basic Productizer for the OpenWeatherMap API using Python and
FastAPI. Serves as an example of how to implement a working Productizer.

## Development

Generic pre-requisites for development

- [Pre-commit](https://pre-commit.com/#install)
- [Python 3.11+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://docs.docker.com/install/)

To set up the `pre-commit` hooks, run `pre-commit install` in the repo. After it you can
manually run `pre-commit` only for your changes or `pre-commit run --all-files` for all
files.

## Running

### Local

Install dependencies:

```shell
poetry install
```

Then to run the application, use:

```shell
poetry run invoke dev
```

### Docker

Make sure [Docker](https://docs.docker.com/install/) is installed.

```shell
docker build -t owm-productizer .
docker run -p 8000:8000 --rm -it owm-productizer
```

## Example API query

```shell
curl -X POST -H "Content-Type: application/json" -d '{"lat":60.192059, "lon":24.945831}' http://localhost:8000/Weather/Current/Metric_v1.0
```

## Testing

To run the tests:

```bash
poetry run invoke test
```

## Docs

The API serves its own docs, if running as instructed above, can be found at
`http://localhost:8000/docs`, and the OpenAPI 3.0 spec can be found at
`http://localhost:8000/openapi.json`.

## License

This code is released under the BSD 3-Clause license. Details in the
[LICENSE.md](./LICENSE.md) file.

## Guides and help

[Written guide for how to build a data source](https://ioxio.com/guides/how-to-build-a-data-source)

You can also check out our YouTube tutorial:

[![Defining Data Products for the IOXIO® Dataspace technology
](https://img.youtube.com/vi/f-f6P_-8zoQ/0.jpg)](http://www.youtube.com/watch?v=f-f6P_-8zoQ)

Also join our [IOXIO Community Slack](https://slack.ioxio.com/)
