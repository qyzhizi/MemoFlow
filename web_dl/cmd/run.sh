#!/bin/bash

# 运行 Python web_dl/cmd/main
python web_dl/cmd/main &

# 运行 Python celery_work.py
python web_dl/cmd/celery_work