from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Customer(models.Model):
    """客户信息表"""
    name = models.CharField(max_length=32, blank=True, null=True, verbose_name='姓名')
    qq = models.CharField(max_length=64, unique=True, verbose_name='联系方式（QQ）')
    phone = models.CharField(max_length=64, blank=True, null=True, verbose_name='电话')
    id_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='身份证号')
    email = models.EmailField(max_length=64, blank=True, null=True, verbose_name='邮箱')
    source_choice = ((0, '转介绍'),
                     (1, 'QQ群'),
                     (2, '官网'),
                     (3, '百度推广'),
                     (4, '51CTO'),
                     (5, '知乎'),
                     (6, '市场推广'))
    source = models.SmallIntegerField(choices=source_choice, verbose_name='来源')
    referral_from = models.CharField(verbose_name="转介绍人QQ", max_length=64, blank=True, null=True)
    consult_course = models.ForeignKey('Course', verbose_name='咨询课程', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='标签')
    content = models.TextField(verbose_name='咨询详情')
    status = models.SmallIntegerField(choices=((0, '已报名'), (1, '未报名')), verbose_name='状态')
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='咨询顾问')
    memo = models.TextField(blank=True, null=True, verbose_name='备忘录')
    date = models.DateTimeField(auto_now_add=True, verbose_name='日期')

    def __str__(self):
        return self.qq

    class Meta:
        verbose_name = '客户信息表'
        verbose_name_plural = '客户信息表'


class Tag(models.Model):
    """标签表"""
    name = models.CharField(unique=True, max_length=32, verbose_name='名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签表'
        verbose_name_plural = '标签表'


class CustomerFollowUp(models.Model):
    """客户跟进记录"""
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='客户')
    content = models.TextField(verbose_name='跟进内容')
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='咨询顾问')
    intention_choice = ((0, '2周内报名'),
                        (1, '1个月内报名'),
                        (2, '近期无报名计划'),
                        (3, '已报名'),
                        (4, '已拉黑'),)
    intention = models.SmallIntegerField(choices=intention_choice, verbose_name='意向')
    date = models.DateTimeField(auto_now_add=True, verbose_name='日期')

    def __str__(self):
        name = '%s:%s' % (self.customer.qq, self.intention)
        return name

    class Meta:
        verbose_name = '客户跟进记录'
        verbose_name_plural = '客户跟进记录'


class Course(models.Model):
    """课程表"""
    name = models.CharField(unique=True, max_length=64, verbose_name='名称')
    price = models.PositiveSmallIntegerField(verbose_name='价格')
    period = models.PositiveSmallIntegerField(verbose_name='周期(月)')
    outline = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '课程表'
        verbose_name_plural = '课程表'


class ContractTemplate(models.Model):
    """合同范本"""
    name = models.CharField(unique=True, max_length=64, verbose_name='合同名称')
    template = models.TextField(verbose_name='合同内容')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '合同范本'
        verbose_name_plural = '合同范本'


class Branch(models.Model):
    """校区表"""
    name = models.CharField(max_length=128, unique=True, verbose_name='名称')
    adder = models.CharField(max_length=128, verbose_name='地址')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '校区表'
        verbose_name_plural = '校区表'


class ClassList(models.Model):
    """班级表"""
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, verbose_name='校区')
    course = models.ForeignKey("Course", on_delete=models.CASCADE, verbose_name='课程')
    class_type = models.SmallIntegerField(choices=((0, "网络"), (1, "面授(周末)"), (2, "面授(脱产)")))
    semester = models.PositiveSmallIntegerField(verbose_name='学期')
    contract = models.ForeignKey('ContractTemplate', on_delete=models.CASCADE, verbose_name='合同')
    teachers = models.ManyToManyField('UserProfile', verbose_name='教师')
    start_date = models.DateField(verbose_name='开班时间')
    end_date = models.DateField(verbose_name='结业时间', blank=True, null=True)

    def __str__(self):
        name = '%s %s %s' % (self.branch, self.course, self.semester)
        return name

    class Meta:
        unique_together = ('branch', 'course', 'semester')
        verbose_name = '班级表'
        verbose_name_plural = '班级表'


class CourseRecord(models.Model):
    """课程记录表"""
    from_class = models.ForeignKey('ClassList', on_delete=models.CASCADE, verbose_name='班级')
    day_num = models.PositiveSmallIntegerField(verbose_name='第几天')
    teacher = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='教师')
    has_homework = models.BooleanField(default=True, verbose_name='是否布置作业')
    homework_title = models.CharField(max_length=128, blank=True, null=True, verbose_name='作业题目')
    homework_content = models.TextField(blank=True, null=True, verbose_name='作业内容')
    outline = models.TextField(verbose_name='本节课程大纲')
    date = models.DateField(auto_now_add=True, verbose_name='日期')

    def __str__(self):
        name = "%s %s" % (self.from_class, self.day_num)
        return name

    class Meta:
        unique_together = ('from_class', 'day_num')
        verbose_name = '课程记录表'
        verbose_name_plural = '课程记录表'


class StudyRecord(models.Model):
    """学习记录表"""
    student = models.ForeignKey('Enrollment', on_delete=models.CASCADE, verbose_name='学生')  # 实际关联为报名表
    course_record = models.ForeignKey('CourseRecord', on_delete=models.CASCADE, verbose_name='课程记录')
    attendance_choice = ((0, '已签到'), (1, '迟到'), (2, '缺勤'), (3, '早退'))
    attendance = models.SmallIntegerField(choices=attendance_choice, default=0, verbose_name='上课情况')
    score_choice = ((100, 'A+'), (90, 'A'), (85, 'B+'),
                    (80, 'B'), (75, 'B-'), (70, 'C+'),
                    (60, 'C'), (40, 'C-'), (-50, 'D'),
                    (-100, 'COPY'), (0, 'N/A'))
    score = models.SmallIntegerField(choices=score_choice, verbose_name='得分')
    memo = models.TextField(blank=True, null=True, verbose_name='备忘录')
    date = models.DateField(auto_now_add=True, verbose_name='日期')

    def __str__(self):
        name = "%s %s %s" % (self.student, self.course_record, self.score)
        return name

    class Meta:
        unique_together = ('student', 'course_record')
        verbose_name = '学习记录表'
        verbose_name_plural = '学习记录表'


class Enrollment(models.Model):
    """报名表"""
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='客户')
    enrolled_class = models.ForeignKey('ClassList', verbose_name='所报班级', on_delete=models.CASCADE)
    consultant = models.ForeignKey("UserProfile", on_delete=models.CASCADE, verbose_name='课程顾问')
    contract_agreed = models.BooleanField(default=False, verbose_name='学员已同意合同条款')
    contract_approved = models.BooleanField(default=False, verbose_name='合同已审核')
    date = models.DateTimeField(auto_now_add=True, verbose_name='日期')

    def __str__(self):
        name = '%s %s' % (self.customer, self.enrolled_class)
        return name

    class Meta:
        unique_together = ("customer", 'enrolled_class')
        verbose_name = '报名表'
        verbose_name_plural = '报名表'


class Payment(models.Model):
    """缴费记录表"""
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='客户')
    course = models.ForeignKey("Course", on_delete=models.CASCADE, verbose_name='课程')
    amount = models.PositiveIntegerField(verbose_name="金额", default=500)
    consultant = models.ForeignKey("UserProfile", on_delete=models.CASCADE, verbose_name='课程顾问')
    date = models.DateTimeField(auto_now_add=True, verbose_name='日期')

    def __str__(self):
        name = "%s %s" % (self.customer, self.amount)
        return name

    class Meta:
        verbose_name = '缴费记录表'
        verbose_name_plural = '缴费记录表'


# class UserProfile(models.Model):
#     """账户表"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=32, verbose_name='姓名')
#     roles = models.ManyToManyField('Role', verbose_name='角色')
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = '账户表'
#         verbose_name_plural = '账户表'


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=32, unique=True, verbose_name='角色名')
    menu = models.ManyToManyField('Menu', blank=True, verbose_name='菜单')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '角色表'
        verbose_name_plural = '角色表'


class Menu(models.Model):
    """菜单名"""
    menu_name = models.CharField(max_length=32, unique=True, verbose_name='菜单名')
    url_type = models.IntegerField(choices=((0, 'alias'), (1, 'absolutely_url')))
    url_name = models.CharField(max_length=64, verbose_name='URL别名')
    order_by = models.SmallIntegerField(choices=((0, '首页'), (1, '数据关系'), (2, '上课管理'), (3, '缴费管理'),
                                                 (4, '系统管理')), verbose_name='排序', null=True)

    def __str__(self):
        return self.menu_name

    class Meta:
        verbose_name_plural = '菜单管理'
        verbose_name = '菜单管理'


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        创建用户
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),  # email验证
            name=name,
        )

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        创建超级用户
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """账户表"""
    email = models.EmailField(
        verbose_name='邮箱账户',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=64, verbose_name='用户名')
    password = models.CharField(_('password'), max_length=128, help_text="""<a href='password/'>修改密码</a>""")
    roles = models.ManyToManyField('Role', verbose_name='角色')
    # date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    is_admin = models.BooleanField(default=False, verbose_name='是否为管理员')
    stu_account = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=True, null=True,
                                    verbose_name='关联学员账号', help_text='学员报名后方可才能创建账户')

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'    # 指定用户名字段
    REQUIRED_FIELDS = ['name']     # 必须填写字段

    class Meta:
        permissions = (
            ("table_objs", "查看客户库表单权限"),
        )

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin
