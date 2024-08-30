from django.http import HttpResponse
from django.urls import path
from rest_framework import routers

from apps.async_task.views.async_task_view import AsyncTaskView

urlpatterns = [
    path('', lambda request: HttpResponse("欢迎访问")),

]
# DRF路由
router = routers.DefaultRouter(trailing_slash=False)

# 异步任务
router.register("async_task", AsyncTaskView, basename="async_task")

urlpatterns += router.urls
