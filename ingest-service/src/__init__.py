import sys, pathlib
# local test path only; container uses PYTHONPATH=/app:/app/proto/gen/python
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent / "proto/gen/python"))
