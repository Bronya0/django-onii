#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django_q.models import Task
from rest_framework.serializers import ModelSerializer

from app.model.async_task.async_task_model import DjangoQProcess


class DjangoQTaskSerializer(ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ["id"]


class DjangoQProcessSerializer(ModelSerializer):

    class Meta:
        model = DjangoQProcess
        fields = '__all__'
        read_only_fields = ["id"]