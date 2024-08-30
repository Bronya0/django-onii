from rest_framework.response import Response
from rest_framework.serializers import Serializer


class SuccessResponse(Response):

    def __init__(self, data=None, msg='操作成功', status=200, code=2000, template_name=None, headers=None, exception=False,
                 content_type='application/json', **kwargs):
        std_data = {
            "code": code,
            "data": data,
            "msg": msg,
        }
        super(SuccessResponse, self).__init__(std_data, status, template_name, headers, exception, content_type)


class ErrorResponse(Response):

    def __init__(self, data=None, msg='操作失败', code=5000, status=200, template_name=None, headers=None,
                 exception=False, content_type='application/json', **kwargs):
        std_data = {
            "code": code,
            "data": data,
            "msg": msg,
        }
        super(ErrorResponse, self).__init__(std_data, status, template_name, headers, exception, content_type)


class DefaultSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
