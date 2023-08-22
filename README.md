# Example Productizer

Implementation of a basic Productizer for the OpenWeatherMap API using Python and
FastAPI. Serves as an example of how to implement a working Productizer.

## Running

The environment is dockerized, so this requires
[Docker](https://docs.docker.com/install/) installed.

```bash
docker build -t owm-productizer .
docker run -p 8000:8000 --env=API_KEY=... --rm -it owm-productizer
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
