"""API server example — serve the kernel over HTTP.

Run:
    pip install 'moac-qmm[api]'
    python examples/05_api_server.py
"""

import uvicorn

from moac_qmm import __version__
from moac_qmm.api import app

if __name__ == "__main__":
    print(f"MOAC QMM API v{__version__} — http://127.0.0.1:8000/docs")
    print("Endpoints: /healthz /readyz /version /v1/simulate /v1/optimize /v1/predict")
    uvicorn.run(app, host="127.0.0.1", port=8000)
