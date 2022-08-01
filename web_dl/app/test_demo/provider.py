#!/usr/bin/env python
# coding=utf-8

from web_dl.common import dependency
from web_dl.common import manager


@dependency.provider('test_api')
class Manager(object):
    driver_namespace = "test_api"

    def __init__(self):
        self.test = 'test'


