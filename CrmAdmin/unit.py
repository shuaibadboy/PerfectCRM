# 此文件中函数为自定义函数

from django.db.models import Q
from django.core.paginator import Paginator


def get_filter_content(request, query_sets, admin_class):
    """获取filter条件及filter后的对象"""
    filter_condition = {}
    for key, val in request.GET.items():
        if key not in ('_page', '_o', '_q'):
            if admin_class.model._meta.get_field(key).get_internal_type() in ('DateField', 'DateTimeField'):
                key = "%s__gte" % key
            if val:
                filter_condition[key] = val
    return query_sets.filter(**filter_condition), filter_condition


def get_page_listing(request, query_sets, admin_class):
    """获取分页后的对象"""
    paginator = Paginator(query_sets, admin_class.list_per_page)   # Show 25 contacts per page
    page = request.GET.get('_page', None)
    query_sets = paginator.get_page(page)
    return query_sets


def get_query_sets_orderby(request, query_sets, admin_class):
    """排序"""
    order_by_conditions = 0
    for key, val in request.GET.items():
        if key == '_o':
            if int(request.GET.get('_o', None)) > 0:
                orderby_index = int(request.GET.get('_o'))-1
                orderby_column = admin_class.list_display[orderby_index]
                query_sets = query_sets.order_by(orderby_column)
            elif int(request.GET.get('_o')) < 0:
                orderby_index = int(request.GET.get('_o')) + 1
                orderby_column = admin_class.list_display[abs(orderby_index)]
                query_sets = query_sets.order_by('-'+orderby_column)
            order_by_conditions = int(request.GET.get('_o'))
    return query_sets, order_by_conditions


def get_search_content(request, query_sets, admin_class):
    """搜索"""
    search_c = ''
    for key, val in request.GET.items():
        if key == '_q':
            search_c = request.GET.get('_q', '')
            q_obj = Q()
            q_obj.connector = 'OR'
            for search_condition in admin_class.search_fields:
                q_obj.children.append(('%s__contains' % search_condition, search_c),)
            query_sets = query_sets.filter(q_obj)
    return query_sets, search_c
