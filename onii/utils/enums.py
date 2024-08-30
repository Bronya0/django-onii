from enum import Enum as Enu


class DescribedEnum(Enu):
    """
    枚举包装
    """

    @property
    def v(self):
        return self.value[0]

    @property
    def desc(self):
        return self.value[1]

    @classmethod
    def get_desc_by_v(cls, v):
        for member in cls:
            if member.v == v:
                return member.desc
        return None

    @classmethod
    def get_v_by_desc(cls, desc):
        for member in cls:
            if member.desc == desc:
                return member.v
        return None

    @classmethod
    def to_dict(cls):
        _dict = {}
        for item in cls:
            _dict[item.v] = item.desc
        return _dict

    @classmethod
    def to_dict_lst(cls):
        lst = []
        for member in cls:
            lst.append({
                "v": member.v,
                "desc": member.desc
            })
        return lst


class Status(DescribedEnum):
    """
    状态枚举
    """
    can_test = 1, "待测试"
    err_validate = 2, "测试未通过"

