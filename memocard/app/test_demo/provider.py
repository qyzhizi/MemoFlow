#!/usr/bin/env python
# coding=utf-8
import os
import logging

from memocard.core import dependency
from memocard.core import manager

LOG = logging.getLogger(__name__)


@dependency.provider('test_api')
class Manager(object):
    driver_namespace = "test_api"

    def __init__(self):
        self.test = 'test'

    def get_html(self):
        # parent_file =  os.path.abspath('./').split('/')[-1]
        # # data
        # data_path = os.path.abspath("../../data")
        # # data/test_demo/test.html
        # html_file = os.path.join(data_path, parent_file, 'test.html')
        # LOG.info(parent_file)
        # LOG.info(data_path)
        # LOG.info(html_file)
        
        with open("data/test_demo/index.html", "r", encoding='UTF-8')as f:
            res = f.read()
        return res

