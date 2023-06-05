#!/bin/bash

# 运行 Python memocard/cmd/main
python memocard/cmd/main &

# 运行 Python celery_work.py
python memocard/cmd/celery_work