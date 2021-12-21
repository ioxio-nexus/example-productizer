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
