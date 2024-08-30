#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from apps.async_task.filters.async_task_filter import AsyncTaskFilter
from apps.async_task.models.async_task_model import DjangoQProcess
from apps.async_task.services.task_service import AsyncTaskService
from utils.drf_util import SuccessResponse
from utils.page_util import MyPageNumberPagination


class AsyncTaskView(GenericViewSet):
    queryset = DjangoQProcess.objects.all().order_by('-id')
    pagination_class = MyPageNumberPagination
    filterset_class = AsyncTaskFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        res = []
        if page is not None:
            names = [_page.task_name for _page in page]
            ats = AsyncTaskService()
            res = ats.get_result_by_names(names)
            return self.get_paginated_response(res)

        return SuccessResponse(res)

    @action(methods=['get'], detail=False)
    def groups(self, request, *args, **kwargs):
        groups = DjangoQProcess.objects.filter(group__isnull=False).values('group').distinct().order_by()
        return SuccessResponse(data=groups)
