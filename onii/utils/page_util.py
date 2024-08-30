#!/usr/bin/env python
# -*-coding:utf-8 -*-
from collections import OrderedDict

from django.core import paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MyPageNumberPagination(PageNumberPagination):
    # 设置url中的页码
    page_query_param = 'page'
    # 设置url中的条数
    page_size_query_param = 'size'
    # 设置每一页的默认数据条数（必选）
    page_size = 10
    # 设置每一页最多可取的数据数（可选）
    max_page_size = 999

    def get_paginated_response(self, data):
        code = 2000
        msg = 'success'
        res = {
            "page": int(self.get_page_number(self.request, paginator)) or 1,
            "total": self.page.paginator.count,
            "size": int(self.get_page_size(self.request)) or 10,
            "data": data
        }
        if not data:
            code = 2000
            msg = "暂无数据"
            res['data'] = []

        return Response(OrderedDict([
            ('code', code),
            ('msg', msg),
            # ('total',self.page.paginator.count),
            ('data', res),
        ]))

