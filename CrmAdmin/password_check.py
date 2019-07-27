import re


class CheckMyPassword:
    """
    分别调用 method_1()、method_2()、method_3() 三种方式进行密码验证
    :message 调用errors 返回错误信息
    :keyword 两次输入的密码
    :return 通过验证返回正确密码，否则返回None
    """
    def __init__(self):
        self.errors = {}

    def check_consistency(self, pwd1, pwd2):
        """验证两次输入的密码是否一致"""
        if pwd1 == pwd2:
            return True
        else:
            self.errors['长度'] = " 两次输入的密码必须一致."
            return False

    def method_1(self, pwd1, pwd2):
        """
        验证方式:
            1.密码长度为8-20位.
            2.密码必须包含至少一个数字、一个大写字母以及一个小写字母.
        """
        pattern = re.compile('^(?=.[a-z])(?=.[A-Z])(?=.*\d)[\s\S]{8,16}$')
        match = pattern.findall(pwd1)
        if self.check_consistency(pwd1, pwd2) and match:
            return pwd1
        else:
            self.errors['1'] = " 密码长度必须大于8."
            self.errors['2'] = " 密码必须包含至少一个数字、一个大写字母以及一个小写字母."
            return None

    def method_2(self, pwd1, pwd2):
        """
        验证方式:
            1.密码必须由字母、数字、特殊符号组成，区分大小写
            2.特殊符号包含（. _ ~ ! @ # $ ^ & *）
            3.密码长度为8-20位
        """
        pattern = re.compile('^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[._~!@#$^&*])[A-Za-z0-9._~!@#$^&*]{8,20}$')
        match = pattern.findall(pwd1)
        if self.check_consistency(pwd1, pwd2) and match:
            return pwd1
        else:
            self.errors['1'] = " 密码必须由字母、数字、特殊符号组成，区分大小写."
            self.errors['2'] = " 特殊符号包含（. _ ~ ! @ # $ ^ & *）"
            self.errors['3'] = " 密码长度为8-20位"
            return None

    def method_3(self, pwd1, pwd2):
        """
        验证方式:
            1.密码必须由字母、数字组成，区分大小写
            2.密码长度为8-20位
        """
        pattern = re.compile('^(?=.*[a-zA-Z])(?=.*[0-9])[A-Za-z0-9]{8,20}$')
        match = pattern.findall(pwd1)
        if self.check_consistency(pwd1, pwd2) and match:
            return pwd1
        else:
            self.errors['1'] = " 密码必须由字母、数字组成，区分大小写."
            self.errors['2'] = " 密码长度为8-20位"
            return None



