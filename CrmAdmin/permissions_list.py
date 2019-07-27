from CrmAdmin import permissions_hook

perm_dic = {
    # 'crm_table_index': ['table_index', 'GET', [], {}, ],  # 可以查看CRM APP里所有数据库表
    'crm_table_objs': ['table_objs', 'GET', [], {}, permissions_hook.my_perm_func],  # 可以查看每张表里所有的数据
    # 'crm_table_list_view': ['table_change', 'GET', [], {}],  # 可以访问表里每条数据的修改页
    # 'crm_table_list_change': ['table_change', 'POST', [], {}],  # 可以对表里的每条数据进行修改
}


