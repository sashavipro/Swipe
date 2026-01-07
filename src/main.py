"""src/main.py."""

import uvicorn
from src.app import create_app
from src.container_factory import create_container

container = create_container()
app = create_app(container)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
