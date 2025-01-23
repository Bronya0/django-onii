import datetime

from django.http import HttpResponse, JsonResponse
from django.urls import path
from rest_framework import routers

from app.api.v1.async_task.async_task_view import AsyncTaskView

urlpatterns = [
    path('', lambda request: JsonResponse({"now": datetime.datetime.now()})),

]
# DRF路由
router = routers.DefaultRouter(trailing_slash=False)

# 异步任务
router.register("async_task", AsyncTaskView, basename="async_task")

urlpatterns += router.urls
