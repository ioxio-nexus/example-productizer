from os import environ

import uvicorn
from invoke import task
from uvicorn.supervisors import ChangeReload


@task
def dev(ctx, port=8000):
    """Runs the API locally on given port.

    :param invoke.Context ctx: The invoke context.
    :param int port: The port to run the API on, defaults to 8000.
    """
    host = "0.0.0.0"  # nosec, it's not a mistake
    port = environ.get("PORT", port)

    config = uvicorn.Config(
        app="app.main:app",
        host=host,
        port=int(port),
        reload=True,
        log_level="debug",
    )
    server = uvicorn.Server(config)

    supervisor = ChangeReload(config, target=server.run, sockets=[config.bind_socket()])
    supervisor.run()


@task
def serve(ctx, port=8000):
    host = "0.0.0.0"  # nosec, it's not a mistake
    port = environ.get("PORT", port)
    server = uvicorn.Server(
        uvicorn.Config(app="app.main:app", host=host, port=int(port)),
    )
    server.run()
