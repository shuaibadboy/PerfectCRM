from django import template
from django.utils.safestring import mark_safe

register = template.Library()   # register的名字是固定的,不可改变


@register.simple_tag
def render_table_name(admin_class):
    """通过admin_class返回表单名"""
    return admin_class.model._meta.verbose_name


@register.simple_tag
def app_return_table_name(admin_app, table_name):
    """通过admin_app返回表单名"""
    return admin_app[table_name].model._meta.verbose_name


@register.simple_tag
def ger_verbose_name(column, admin_table):
    """返回column的verbose_name"""
    model_class = admin_table.model
    if hasattr(model_class, column):
        return model_class._meta.get_field(column).verbose_name.upper()
    else:
        return getattr(admin_table, column).verbose_name.upper()


@register.simple_tag
def judge_column_in_fields(column, admin_table):
    if hasattr(admin_table.model, column):
        return True
    else:
        return False


@register.simple_tag
def bulid_table_row(request, query_set, admin_class):
    """展示表单数据"""
    column_list = admin_class.list_display
    model_class = admin_class.model
    row_ele = ''
    if column_list:
        for column in column_list:
            if hasattr(model_class, column):
                field_obj = query_set._meta.get_field(column)
                if field_obj.choices:
                    column_data = getattr(query_set, 'get_%s_display' % column)()
                else:
                    column_data = getattr(query_set, column)
            else:
                field_obj_func = getattr(admin_class, column)
                admin_class.instance = query_set
                admin_class.request = request
                column_data = field_obj_func()
            if column == column_list[0]:
                row_ele += '<td><a href="%s%s/change/">%s</a></td>' % (request.path, query_set.id, column_data)
            else:
                row_ele += '<td>%s</td>' % column_data
    else:
        row_ele = '<td><a href="%s%s/change/">%s</a></td>' % (request.path, query_set.id, query_set)
    row_ele += '<td><a href="%s%s/change/"><span class="glyphicon glyphicon-pencil" aria-hidden="true">编辑' \
               '</span></a></td>' % (request.path, query_set.id)
    return mark_safe(row_ele)


@register.simple_tag
def bulid_filter_ele(filter_column, admin_class):
    """创建筛选框"""
    import datetime
    filter_list = admin_class.model.objects.all().values(filter_column)
    filter_field = admin_class.model._meta.get_field(filter_column)
    filter_ele = ''
    filter_conditions = admin_class.filter_conditions
    try:
        for ele in filter_field.get_choices():
            if filter_column in filter_conditions:
                if filter_conditions[filter_column] == str(ele[0]):
                    filter_ele += '<option value="%s" selected = "selected">%s</option>' % ele
                else:
                    filter_ele += '<option value="%s">%s</option>' % ele
            else:
                filter_ele += '<option value="%s">%s</option>' % ele
    except AttributeError:
        if filter_field.get_internal_type() in ('DateField', 'DateTimeField'):
            now_time = datetime.datetime.now()
            datetime_key = "%s__gte" % filter_column
            data_list = (('', "--------"),
                         (now_time.strftime("%Y-%m-%d"), "今天"),
                         ((now_time - datetime.timedelta(7)).strftime("%Y-%m-%d"), "7天内"),
                         ((now_time - datetime.timedelta(30)).strftime("%Y-%m-%d"), "30天内"),
                         ((now_time - datetime.timedelta(90)).strftime("%Y-%m-%d"), "90天内"),
                         (now_time.replace(month=1, day=1).strftime("%Y-%m-%d"), "本年内"))
            for i in data_list:
                if datetime_key in filter_conditions:
                    if i[0] == filter_conditions[datetime_key]:
                        filter_ele += "<option value='%s' selected='selected'>%s</option>" % i
                    else:
                        filter_ele += "<option value='%s'>%s</option>" % i
                else:
                    filter_ele += "<option value='%s'>%s</option>" % i
        else:
            filter_ele = '<option value="">--------</option>'
            for ele in filter_list:
                if filter_column in filter_conditions:
                    if filter_column[ele] == ele:
                        filter_ele += '<option value="%s" selected = "selected">%s</option>' % (ele[filter_column], ele[filter_column])
                else:
                    filter_ele += '<option value="%s">%s</option>' % (ele[filter_column], ele[filter_column])
    filter_select = '%s:<select name="%s" class="form-control input-sm">%s</select>' % (filter_column, filter_column, filter_ele)
    return mark_safe(filter_select)


@register.simple_tag
def get_model_name(admin_class):
    """获取__str__()"""
    model_class = admin_class.model
    column_name = model_class._meta.model_name
    return column_name.title()


@register.simple_tag
def get_web_pagination(query_sets, admin_class):
    """分页元素"""
    previous_page_number = ''
    filter_dir = get_filtered_args(admin_class)
    order_condition = admin_class.orderby_conditions
    if query_sets.has_previous():
        previous_page_number = query_sets.number - 1
    page_ele = """<nav aria-label="Page navigation">
                  <ul class="pagination">
                    <li><a href="?_page=1&_o=%s&_q=%s%s">&laquo; 首页</a><a href="?_page= %s&_o=%s&_q=%s%s">上一页</a>
                    </li>
                    """ % (order_condition, admin_class.search_conditions, filter_dir, previous_page_number,
                           order_condition, admin_class.search_conditions, filter_dir)
    for i in query_sets.paginator.page_range:
        active = ''
        if abs(query_sets.number - i) < 5:
            if query_sets.number == i:
                active = 'active'
            page_ele += """<li class="%s"><a href="?_page= %s&_o=%s&_q=%s%s">%s</a></li>""" % \
                        (active, i, order_condition, filter_dir, admin_class.search_conditions, i)
    if query_sets.has_next():
        next_page_number = query_sets.number + 1
    else:
        next_page_number = query_sets.number
    page_ele += """<li>
    <a href="?_page=%s&_o=%s&_q=%s%s">下一页</a>
    <a href="?_page=%s&_o=%s&_q=%s%s">尾页 &raquo;</a></li></ul></nav>""" \
                % (next_page_number, order_condition, filter_dir, admin_class.search_conditions,
                   query_sets.paginator.num_pages, order_condition, admin_class.search_conditions, filter_dir)
    return mark_safe(page_ele)


@register.simple_tag
def get_list_index(admin_class, column):
    """获取列表元素下标"""
    orderby_index = admin_class.list_display.index(column)+1
    if admin_class.orderby_conditions < 0:
        return 0
    if admin_class.orderby_conditions == orderby_index:
        orderby_index = -orderby_index
    return orderby_index


@register.simple_tag
def render_sorted_arrow(admin_class, column):
    """创建排序箭头"""
    if admin_class.list_display.index(column)+1 == abs(admin_class.orderby_conditions):
        if admin_class.orderby_conditions < 0:
            return mark_safe('<span class="glyphicon glyphicon-sort-by-alphabet-alt" aria-hidden="true"></span>')
        elif admin_class.orderby_conditions > 0:
            return mark_safe('<span class="glyphicon glyphicon-sort-by-alphabet" aria-hidden="true"></span>')
        else:
            return mark_safe('<span></span>')
    else:
        return mark_safe('<span></span>')


@register.simple_tag
def get_filtered_args(admin_class):
    """获取本页面筛选范围"""
    condition_url = ''
    condition = admin_class.filter_conditions
    if condition:
        for key, value in condition.items():
            condition_url += '&%s=%s' % (key, value)
    return condition_url


@register.simple_tag
def get_m2m_obj(admin_class, field, modelform):
    """返回所有未选ManyToMany的选项"""
    all_obj = getattr(admin_class.model, field.name).rel.model.objects.all()
    standby_obj = []
    try:
        selected_obj = getattr(modelform.instance,  field.name).all()
    except ValueError:
        selected_obj = []
    for obj in all_obj:
        if obj not in selected_obj:
            standby_obj.append(obj)
    return standby_obj


@register.simple_tag
def get_m2m_select_obj(modelform, field):
    """返回所有已选ManyToMany的选项"""
    try:
        standby_obj = getattr(modelform.instance, field.name).all()
    except ValueError:
        standby_obj = []
    return standby_obj


@register.simple_tag
def display_all_related_objs(obj):
    ele = """<li>%s:<a href='/crm-admin/%s/%s/%s/change/'>%s</a><ul>""" % (obj._meta.verbose_name, obj._meta.app_label,
                                                         obj._meta.model_name, obj.id, obj)
    if obj._meta.related_objects:
        for reversed_m2m_obj in obj._meta.related_objects:
            reversed_m2m_name = '_'.join([reversed_m2m_obj.name, 'set'])
            related_objs = getattr(obj, reversed_m2m_name).all()
            for related_obj in related_objs:
                return_ele = display_all_related_objs(related_obj)
                ele += return_ele
    if obj._meta.many_to_many:
        model_name = obj._meta.model_name
        for reversed_m2m_obj in obj._meta.many_to_many:
            reversed_m2m_name = reversed_m2m_obj.name
            related_objs = getattr(obj, reversed_m2m_name).all()
            for obj in related_objs:
                ele += """<li>%s-%s关系：%s</li>""" % (model_name, obj._meta.model_name, obj)
    ele += '</ul></li>'
    return mark_safe(ele)


@register.simple_tag
def ger_action_select_option(admin_class):
    ele = '<option value="">--------</option>'
    for action in admin_class.actions:
        vn = getattr(admin_class, action)
        ele += '<option value="%s">%s</option>' % (action, vn.verbose_name if hasattr(vn, 'verbose_name') else action)
    return mark_safe(ele)
