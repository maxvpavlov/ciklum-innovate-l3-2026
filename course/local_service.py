"""Launch a trusted course service on an ephemeral loopback port for demos."""
from contextlib import asynccontextmanager
import asyncio
import os
import socket
import sys
import tempfile
import httpx


@asynccontextmanager
async def local_service(module, health_path="/health"):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    env = dict(os.environ, A2A_BASE_URL=url, MODEL_PROVIDER="mock")
    with tempfile.TemporaryFile() as log:
        process = await asyncio.create_subprocess_exec(sys.executable, "-m", "uvicorn",
            module, "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning",
            env=env, stdout=log, stderr=log)
        try:
            async with httpx.AsyncClient(timeout=.3) as client:
                for _ in range(300):
                    if process.returncode is not None:
                        log.seek(0)
                        raise RuntimeError(log.read().decode()[-4000:])
                    try:
                        if (await client.get(url+health_path)).status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    await asyncio.sleep(.1)
                else:
                    raise RuntimeError("local_service_start_timeout")
            yield url
        finally:
            if process.returncode is None:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), 5)
                except TimeoutError:
                    process.kill(); await process.wait()

