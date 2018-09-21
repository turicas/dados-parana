from pathlib import Path


BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "data"
DOWNLOAD_PATH = DATA_PATH / "download"
OUTPUT_PATH = DATA_PATH / "output"
LOG_PATH = DATA_PATH / "log"

for path in (DATA_PATH, DOWNLOAD_PATH, OUTPUT_PATH, LOG_PATH):
    if not path.exists():
        path.mkdir()
