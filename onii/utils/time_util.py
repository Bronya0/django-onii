#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import datetime


class TimeUtil:
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATETIME_FORMAT_MS = '%Y.%m.%d_%H.%M.%S.%f'
    FORMAT_DATETIME2 = "%Y-%m-%d_%H_%M_%S"
    FORMAT_DATETIME3 = "%Y-%m-%d"
    FORMAT_DATETIME4 = "%Y-%m-%d %H:00:00"
    FORMAT_DATETIME5 = "%Y-%m-%d 00:00:00"
    FORMAT_DATETIME6 = "%m-%d"
    FORMAT_DATETIME7 = "yyyy-MM-dd HH:mm:ss"

    def timestamp_to_datetime(self, timestamp):
        """时间戳转datetime类型"""
        return datetime.datetime.fromtimestamp(timestamp)

    def datetime_to_timestamp(self, dt):
        """datetime类型转时间戳"""
        return int(time.mktime(dt.timetuple()))

    def datetime_to_str(self, dt, fmt=DATETIME_FORMAT):
        """datetime类型转字符串"""
        return dt.strftime(fmt)

    def str_to_datetime(self, dt_str, fmt=DATETIME_FORMAT):
        """字符串转datetime类型"""
        return datetime.datetime.strptime(dt_str, fmt)

    def timestamp_to_str(self, timestamp, fmt=DATETIME_FORMAT):
        """时间戳转时间字符串"""
        return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)

    def str_to_timestamp(self, dt_str, fmt=DATETIME_FORMAT):
        """时间字符串转时间戳"""
        return int(time.mktime(time.strptime(dt_str, fmt)))

    def get_now_datetime(self):
        """获取当前时间(datetime)"""
        return datetime.datetime.now()

    def get_now_timestamp(self):
        """时间戳(int)"""
        return int(time.time())

    def get_now_time_str(self, fmt=DATETIME_FORMAT):
        """获取当前时间字符串"""
        return datetime.datetime.now().strftime(fmt)

    def get_00_time(self, time_):
        """获取某天00:00:00时间"""
        date_time = self.is_datetime_or_int_str(time_)
        start_time = date_time.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_time

    def get_23_time(self, time_):
        """获取某天23:59:59时间"""
        date_time = self.is_datetime_or_int_str(time_)
        end_time = date_time.replace(hour=23, minute=59, second=59, microsecond=0)
        return end_time

    def get_some_day_st_et(self, time_):
        """
            获取某天的开始时间与结束时间
            time_:"2024-08-15"/"2024-08-15 11:11:11"/int/datetime
        """
        date_time = self.is_datetime_or_int_str(time_)
        start_time = self.get_00_time(date_time)
        end_time = self.get_23_time(date_time)
        return start_time, end_time

    def get_yesterday_datetime(self):
        """获取前一天的开始时间与结束时间"""
        now = datetime.datetime.now()
        return self.get_some_day_st_et(now)

    # 获取前一天的开始时间戳与结束时间戳
    def get_yesterday_time_stamp(self):
        """获取前一天的开始时间戳与结束时间戳"""
        start_time, end_time = self.get_yesterday_datetime()
        return self.datetime_to_timestamp(start_time), self.datetime_to_timestamp(end_time)

    def get_yesterday_time_str(self, fmt=DATETIME_FORMAT):
        """获取前一天的开始时间与结束时间"""
        start_time, end_time = self.get_yesterday_datetime()
        return self.datetime_to_str(start_time, fmt), self.datetime_to_str(end_time, fmt)

    def get_time_dif(self, t1, t2):
        """获取时间差(秒)"""
        t1 = self.is_datetime_or_int_str(t1)
        t2 = self.is_datetime_or_int_str(t2)
        return (t1 - t2).total_seconds()

    def is_datetime_or_int_str(self, time_):
        if isinstance(time_, datetime.datetime):
            return time_
        elif isinstance(time_, int):
            return self.timestamp_to_datetime(time_)
        elif isinstance(time_, str):
            try:
                return self.str_to_datetime(time_)
            except:
                try:
                    return self.str_to_datetime(time_, fmt=self.FORMAT_DATETIME3)
                except:
                    return None
        else:
            return None


if __name__ == '__main__':
    t = TimeUtil()
    print(t.get_yesterday_datetime())
    print(t.get_yesterday_time_str())
    print(t.get_yesterday_time_stamp())
    print(t.get_some_day_st_et("2024-08-01 11:11:11"))
    print(t.get_now_datetime())
    print(t.get_now_timestamp())
    print(t.get_now_time_str())
