import logging
import traceback
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status

from utils.drf_util import ErrorResponse

LOGGER = logging.getLogger("django")


def exception_handler(exc, context):
    """
    自定义的异常处理方法
    :param exc:
    :param context:
    :return:
    """
    response = drf_exception_handler(exc, context)

    if response is None:
        try:
            context.get('view').raise_uncaught_exception(exc)
        except Exception as e:
            LOGGER.error("view:%s, error:%s", context.get('view'), exc)
            LOGGER.error(traceback.format_exc())
        return ErrorResponse(data="服务器内部错误")
    if response.status_code == status.HTTP_403_FORBIDDEN:
        return ErrorResponse(data="您没有权限进行此操作", code=4003)
    elif response.status_code == status.HTTP_400_BAD_REQUEST:
        return ErrorResponse(msg=response.data, code=4000, data=response.data)
    return response
