from django.urls import resolve
from django.shortcuts import render, redirect, HttpResponse
from CrmAdmin.permissions_list import perm_dic
from django.conf import settings


def perm_check(*args, **kwargs):
    request = args[0]
    resolve_url_obj = resolve(request.path)
    current_url_name = resolve_url_obj.url_name  # 当前url的url_name
    # print('---perm:', request.user, request.user.is_authenticated, current_url_name)
    # match_flag = False
    match_key = None
    if request.user.is_authenticated is False:
        return redirect(settings.LOGIN_URL)
    for permission_key, permission_val in perm_dic.items():
        match_results = None
        per_url_name = permission_val[0]
        per_method = permission_val[1]
        perm_args = permission_val[2]
        perm_kwargs = permission_val[3]
        my_perm_func = None if len(permission_val) == 4 else permission_val[4]
        if per_url_name == current_url_name:    # matches current request url
            if per_method == request.method:    # matches request method
                request_method_func = getattr(request, per_method)  # 获取request.GET/POST
                if perm_args:   # if no args defined in perm dic, then set this request to passed perm
                    # 逐个匹配参数，看每个参数时候都能对应的上。
                    args_matched = False    # for args only
                    for item in perm_args:
                        if request_method_func.get(item, None):     # request字典中有此参数
                            args_matched = True
                        else:
                            # print("arg not match......")
                            args_matched = False
                            break  # 有一个参数不能匹配成功，则判定为假，退出该循环。
                else:
                    args_matched = True
                if perm_kwargs:
                    # 匹配有特定值的参数
                    kwargs_matched = False
                    for k, v in perm_kwargs.items():
                        arg_val = request_method_func.get(k, None)  # request字典中有此参数
                        # print("perm kwargs check:", arg_val, type(arg_val), v, type(v))
                        if arg_val == str(v):   # 匹配上了特定的参数 及对应的 参数值， 比如，需要request 对象里必须有一个叫 user_id=3的参数
                            kwargs_matched = True
                        else:
                            kwargs_matched = False
                            break   # 有一个参数不能匹配成功，则判定为假，退出该循环。
                else:
                    kwargs_matched = True
                if my_perm_func:
                    func_matched = my_perm_func(request, args, kwargs)
                else:
                    func_matched = True
                match_results = [args_matched, kwargs_matched, func_matched]
                # print("--->match_results ", match_results)
                if all(match_results):  # 都匹配上了
                    match_key = permission_key
                    break

    if all(match_results):
        app_name, *per_name = match_key.split('_')
        a = match_key.replace('_', '.', 1)
        # print("--->matched ", match_results, match_key)
        # print(app_name, *per_name)
        perm_obj = '%s.%s' % (app_name, match_key)
        if request.user.has_perm(perm_obj):
            # print('当前用户有此权限')
            return True
        else:
            # print('当前用户没有该权限')
            return False
    else:
        # print("未匹配到权限项，当前用户无权限")
        return False


def check_permission(func):
    def inner(*args, **kwargs):
        if not perm_check(*args, **kwargs):
            request = args[0]
            return render(request, 'crmadmin/page_403.html')
        return func(*args, **kwargs)
    return inner
