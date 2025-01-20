import time


class TimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        duration = (end_time - start_time) * 1000

        # 打印接口耗时
        print(f"\033[34m{request.method} {request.path}\033[0m 耗时 \033[34m{duration:.0f}\033[0m ms")
        return response
