#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime


def demo_task():
    print("定时任务测试", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def demo_async_task(a, b):
    s = f"{a}{b}"
    print("异步任务测试", a, b, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return s