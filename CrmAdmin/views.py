from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.forms import ValidationError
from django.core.paginator import Paginator
from django.contrib.auth import authenticate
# Create your views here.
from CrmAdmin import crmadmin
from CrmAdmin import unit
from CrmAdmin import forms
from CrmAdmin import password_check
from CrmAdmin.permissions import check_permission
from crm import models


@login_required
def index(request):
    data_list = {'table_list': crmadmin.enabled_admins}
    return render(request, 'crmadmin/table_index.html', data_list)


@login_required
def password_reset(request, app, table, obj_id):
    errors = {}
    admin_table = crmadmin.enabled_admins[app][table]
    obj = admin_table.model.objects.get(id=obj_id)
    if request.method == 'POST':
        _password0 = request.POST.get('password0')
        # if not authenticate(username=obj.email, password=_password0):
        #     errors = {'1': '原始密码不匹配'}
        #     return render(request, 'crmadmin/password_reset.html', {"obj": obj, 'errors': errors})
        _password1 = request.POST.get('password1')
        _password2 = request.POST.get('password2')
        cp = password_check.CheckMyPassword()
        password = cp.method_3(_password1, _password2)
        if password:
            obj.set_password(password)
            obj.save()
            return redirect(request.path.rstrip('password/'))
        errors = cp.errors
    return render(request, 'crmadmin/password_reset.html', {"obj": obj, 'errors': errors})


@login_required
def tables_of_app(request, app):
    admin_app = crmadmin.enabled_admins[app]
    return render(request, 'crmadmin/table_of_app.html', {'admin_app': admin_app, 'app_name': app})


@check_permission
@login_required
def display_table_objs(request, app, table):
    """获取数据并按需求展示"""
    admin_table = crmadmin.enabled_admins[app][table]
    query_sets = []
    if request.method == 'GET':
        query_sets = admin_table.model.objects.all().order_by(admin_table.default_order_by)
        query_sets, admin_table.search_conditions = unit.get_search_content(request, query_sets, admin_table)  # 搜索
        query_sets, admin_table.filter_conditions = unit.get_filter_content(request, query_sets, admin_table)  # 筛选
        query_sets, admin_table.orderby_conditions = unit.get_query_sets_orderby(request, query_sets, admin_table)  # 排序
        query_sets = unit.get_page_listing(request, query_sets, admin_table)  # 分页
        return render(request, 'crmadmin/table.html', {'admin_table': admin_table, 'query_sets': query_sets,
                                                       'app_name': app, 'table_name': table})
    elif request.method == 'POST':
        selected_id_list = request.POST.get('selected_id_list', None)
        if selected_id_list:
            selected_id_list = selected_id_list.split(',')
        else:
            selected_id_list = []
        action = request.POST.get('action', None)
        request._action = action
        if hasattr(admin_table, action):
            action = getattr(admin_table, action)
        if selected_id_list:
            query_sets = admin_table.model.objects.filter(id__in=selected_id_list)
        return action(request, query_sets)


@login_required
def table_obj_change(request, app, table, obj_id):
    admin_table = crmadmin.enabled_admins[app][table]
    obj = crmadmin.enabled_admins[app][table].model.objects.get(id=obj_id)
    modelform_class = forms.create_model_forms(admin_table)
    if request.method == 'GET':
        modelform = modelform_class(instance=obj)
    elif request.method == 'POST':
        modelform = modelform_class(request.POST, instance=obj)
        if modelform.is_valid():
            modelform.save()
            redirect_path = '/'.join(request.path.split('/')[0:-3])
            return redirect(redirect_path)
    return render(request, 'crmadmin/table_obj_change.html', {'admin_table': admin_table, 'modelform': modelform,
                                                              'app_name': app, 'table_name': table, 'obj_id': obj_id})


@login_required
def table_obj_add(request, app, table):
    admin_table = crmadmin.enabled_admins[app][table]
    modelform_class = forms.create_model_forms(admin_table, form_add=True)
    if request.method == 'GET':
        modelform = modelform_class()
    elif request.method == 'POST':
        modelform = modelform_class(request.POST)
        if modelform.is_valid():
            modelform.save()
            redirect_path = request.path.replace('add/', '')
            return redirect(redirect_path)
    return render(request, 'crmadmin/table_obj_add.html', {'admin_table': admin_table, 'modelform': modelform})


@login_required
def table_obj_delete(request, app, table, obj_id):
    errors = {'error': 'This is a readonly table'}
    admin_table = crmadmin.enabled_admins[app][table]
    delete_obj = admin_table.model.objects.get(id=obj_id)
    if request.method == 'POST':
        if not admin_table.readonly_table:
            delete_obj.delete()
            return redirect('/crm-admin/%s/%s/' % (app, table))
    return render(request, 'crmadmin/table_obj_delete.html', {'admin_table': admin_table, 'delete_obj': delete_obj,
                                                              'app_name': app, 'table_name': table, 'obj_id': obj_id,
                                                              'errors': errors})
