from os import environ

import uvicorn
from invoke import task


@task
def dev(ctx, port=8000):
    """Runs the API locally on given port.

    :param invoke.Context ctx: The invoke context.
    :param int port: The port to run the API on, defaults to 8000.
    """
    port = environ.get("PORT", port)
    ctx.run(f"uvicorn app.main:app --host 0.0.0.0 --port {port} --reload")


@task
def serve(ctx, port=8000):
    host = "0.0.0.0"  # nosec, it's not a mistake
    port = environ.get("PORT", port)
    server = uvicorn.Server(
        uvicorn.Config(app="app.main:app", host=host, port=int(port)),
    )
    server.run()
