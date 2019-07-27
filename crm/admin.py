from django.contrib import admin
from django.shortcuts import render, redirect, HttpResponse
from django.db import IntegrityError
from django import forms
from crm import models
# Register your models here.


from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField


admin.site.register(models.Menu)
admin.site.register(models.Role)
admin.site.register(models.Tag)


@admin.register(models.Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "adder")
    ordering = ("name",)


@admin.register(models.ClassList)
class ClassListAdmin(admin.ModelAdmin):
    list_display = ("branch", "course", 'class_type', 'semester')
    search_fields = ("course", 'class_type', 'semester', 'teachers')
    list_filter = ("branch", 'class_type', 'semester', 'start_date', 'end_date')
    ordering = ("branch",)


@admin.register(models.CourseRecord)
class CourseRecordAdmin(admin.ModelAdmin):
    list_display = ("from_class", "day_num", 'teacher', 'has_homework', 'date')
    search_fields = ("from_class", 'teacher', 'date', 'outline', 'homework_title')
    list_filter = ("from_class", "day_num", 'teacher', 'has_homework', 'date')
    ordering = ("from_class", "day_num")
    actions = ['initialize_studyrecord']

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
    initialize_studyrecord.short_description = "初始化上课记录"


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "price", 'period')
    search_fields = ("name", "price")
    list_filter = ("name", "price", 'period')
    ordering = ("name",)


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("qq", "name", 'source', 'consultant', 'status', 'date')
    search_fields = ("qq", "name")
    list_filter = ('source', 'consultant', 'date', 'consult_course')
    ordering = ("date", 'consult_course')


@admin.register(models.CustomerFollowUp)
class CustomerFollowUpAdmin(admin.ModelAdmin):
    list_display = ("customer", "consultant", 'date', 'consultant', 'intention', 'date')
    search_fields = ("customer", "content", 'consultant', 'date')
    list_filter = ('intention', 'date', 'consultant')
    ordering = ('date', 'intention', 'consultant')


@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("customer", "enrolled_class", 'consultant', 'contract_agreed', 'contract_approved', 'date')
    search_fields = ("customer", "enrolled_class", 'consultant', 'date')
    list_filter = ("enrolled_class", 'consultant', 'contract_agreed', 'contract_approved', 'date')
    ordering = ('date', 'contract_agreed', 'contract_approved')


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("customer", "course", 'amount', 'consultant', 'date')
    search_fields = ("customer", "course", 'amount', 'consultant', 'date')
    list_filter = ("course", 'amount', 'consultant', 'date')
    ordering = ('date',)


@admin.register(models.StudyRecord)
class StudyRecordAdmin(admin.ModelAdmin):
    list_display = ("student", 'course_record', "attendance", 'score', 'date')
    search_fields = ("student", 'date')
    list_filter = ("attendance", 'score', 'course_record', 'date')
    ordering = ('date', 'score')


# @admin.register(models.UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ("email", "name")
#     search_fields = ("email", "name")
#     # list_filter = ('roles',)
#     ordering = ('email', 'name')


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='输入密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    class Meta:
        model = models.UserProfile
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.UserProfile
        fields = ('email', 'password', 'name', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_admin', 'stu_account')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'roles', 'user_permissions', 'groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


# Now register the new UserAdmin...
admin.site.register(models.ContractTemplate)
admin.site.register(models.UserProfile, UserProfileAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
