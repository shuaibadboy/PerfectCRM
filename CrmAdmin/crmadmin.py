from crm import models
from django.shortcuts import render, redirect, HttpResponse
from django.db import IntegrityError
enabled_admins = {}


class BaseAdmin(object):
    list_display = ()   # 字段为表单字段 或者 表单中的函数
    search_fields = ()
    list_filter = ()
    ordering = ()
    list_per_page = 20
    default_order_by = '-id'
    actions = ['delete_selected_objs']
    filter_horizontal = ()  # Manytomany多选框
    readonly_fields = []
    readonly_table = False
    modelform_exclude_fields = []

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        errors = {"error": "This is a readonly table"}
        if not request.POST.get('delete_html', None):
            selected_id_list = [str(i[0]) for i in querysets.values_list('id')]
            selected_id_list = ','.join(selected_id_list)
            return render(request, 'crmadmin/table_objs_delete.html', {'admin_table': self, 'query_sets': querysets,
                                                                       'app_name': app_name, 'table_name': table_name,
                                                                       'selected_id_list': selected_id_list,
                                                                       'action': request._action, 'errors': errors})
        else:
            selected_id_list = request.POST.get('selected_id_list', None)
            if selected_id_list:
                selected_id_list = selected_id_list.split(',')
            else:
                selected_id_list = []
            query_sets = self.model.objects.filter(id__in=selected_id_list)
            query_sets.delete()
            return redirect('/crm-admin/%s/%s' % (app_name, table_name))
    delete_selected_objs.verbose_name = '删除选中的数据'


class CustomerAdmin(BaseAdmin):
    list_display = ('qq', 'name', 'consult_course', 'status', 'enroll')
    list_filter = ('status', 'consult_course', 'source', 'consultant', 'date')
    search_fields = ('name', 'qq', )
    list_per_page = 20
    filter_horizontal = ('tags',)
    readonly_fields = ('consultant',)
    readonly_table = False
    # actions = ['func1', 'func2']

    def enroll(self):
        message = '报名'
        if self.instance.status == 0:
            message = '报名新课程'
        ele = """<a href='/crm/customer/%s/enrollment/'>%s</a>""" % (self.instance.id, message)
        return ele
    enroll.verbose_name = '报名链接'


class CourseRecordAdmin(BaseAdmin):
    list_display = ("from_class", "teacher", 'has_homework', 'day_num', 'date')
    list_filter = ('from_class', 'has_homework', 'teacher', 'day_num')
    search_fields = ('from_class',)
    list_per_page = 20
    actions = ['delete_selected_objs', 'initialize_studyrecord']

    def initialize_studyrecord(self, request, queryset):
        if len(queryset) > 1:
            return HttpResponse('初始化上课记录时，只能选择一个上课记录表！')
        enrollments = queryset[0].from_class.enrollment_set.all()
        new_studyrecord_list = []
        for enrollment in enrollments:
            new_studyrecord_list.append(models.StudyRecord(student=enrollment, course_record=queryset[0],
                                                           attendance=0, score=0))
        try:
            models.StudyRecord.objects.bulk_create(new_studyrecord_list)
        except IntegrityError:
            return HttpResponse('<h1>批量创建上课记录失败，请检查部分记录是否已经存在</h1>')
        new_path = request.path.replace('courserecord', 'studyrecord') + '?course_record=%s' % queryset[0].id
        return redirect(new_path)
    initialize_studyrecord.verbose_name = "初始化上课记录"


class BranchAdmin(BaseAdmin):
    list_display = ("name",)
    readonly_table = False


class RoleAdmin(BaseAdmin):
    filter_horizontal = ('menu',)


class StudyRecordAdmin(BaseAdmin):
    list_display = ("student", 'course_record', "attendance", 'score', 'date')
    search_fields = ('date',)
    list_filter = ("attendance", 'score', 'course_record', 'date')
    list_per_page = 50


class UserProfileAdmin(BaseAdmin):
    list_display = ("email", "is_active", 'is_admin', 'stu_account')
    readonly_fields = ['password']
    filter_horizontal = ('groups', 'user_permissions', 'roles')
    modelform_exclude_fields = ('last_login',)


def register(models_class, admin_class=None):
    app_name = models_class._meta.app_label
    model_name = models_class._meta.model_name
    if not admin_class:     # 避免多个models共享同一个Admin
        admin_class = BaseAdmin()
    else:
        admin_class = admin_class()
    admin_class.model = models_class  # 将model_class赋值给admin_class
    if app_name not in enabled_admins:
        enabled_admins[app_name] = {}
    enabled_admins[app_name][model_name] = admin_class


register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp)
register(models.Course)
register(models.CourseRecord, CourseRecordAdmin)
register(models.StudyRecord, StudyRecordAdmin)
register(models.ClassList)
register(models.ContractTemplate)
register(models.Enrollment)
register(models.Payment)
register(models.Branch, BranchAdmin)
register(models.Tag)
register(models.Role, RoleAdmin)
register(models.Menu)
register(models.UserProfile, UserProfileAdmin)
