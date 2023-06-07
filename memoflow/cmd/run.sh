#!/bin/bash

# 运行 Python memoflow/cmd/main
python memoflow/cmd/main &

# 运行 Python celery_work.py
python memoflow/cmd/celery_work