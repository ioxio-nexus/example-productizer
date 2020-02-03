# IHAN Productizer example

Implementation of a basic IHAN Productizer for the OpenWeatherMap API using Python (PyPy) and FastAPI.
Serves as an example of how to implement a working Productizer.

## Running

The environment is dockerized, so this requires [Docker](https://docs.docker.com/install/) installed.

```bash
docker build -t owm-productizer .
docker run -p 8000:8000/tcp --rm -it owm-productizer
```

## Docs

The API serves its own docs, if running as instructed above, can be found at `http://localhost:8080/docs`, and the 
OpenAPI 3.0 spec can be found at `http://localhost:8080/openapi.json` (replace `localhost` with value from `minikube ip`
if running Docker in Minikube).

For simplicity's sake these are also hosted in the `gh-pages` branch of this repository. 

## License

This code is released under the BSD 3-Clause license. Details in the [LICENSE.md](./LICENSE.md) file.
