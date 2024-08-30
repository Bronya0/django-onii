#!/usr/bin/env python
# -*-coding:utf-8 -*-
from io import BytesIO

from django.http import HttpResponse
from django.utils.encoding import escape_uri_path


def export_excel(wb, filename):
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        escape_uri_path("{}.xlsx".format(filename))
    )
    response.write(output.getvalue())
    return response
