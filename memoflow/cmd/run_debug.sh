#!/bin/bash

# 运行 Python memoflow/cmd/main
python memoflow/cmd/celery_work > celery_work.log 2>&1 &

# 运行 Python celery_work.py
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client  memoflow/cmd/main