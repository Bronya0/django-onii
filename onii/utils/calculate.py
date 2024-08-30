#!/usr/bin/env python
# -*- coding: utf-8 -*-


def calculate_percentage(numerator, denominator):
    if denominator == 0:  # 处理分母为0的情况
        return "0.00%"
    result = (numerator / denominator) * 100
    return "{:.2f}%".format(result)

