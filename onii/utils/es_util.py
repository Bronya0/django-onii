#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

from onii.settings import YAML_CONF


class EsUtil:

    def __init__(self):
        self.es = Elasticsearch([YAML_CONF['es']], timeout=300)
