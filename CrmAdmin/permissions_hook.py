

def my_perm_func(request, *args, **kwargs):
    # print('perm test', request, args, kwargs)
    consultant_id = request.GET.get('consultant')   # 自定义需要的参数
    if consultant_id:
        consultant_id = int(consultant_id)
    if consultant_id == request.user.id:
        # print("\033[31;1mchecking [%s]'s own customers, pass..\033[0m" % request.user)
        return True
    else:
        # print("\033[31;1muser can only view his's own customer...\033[0m")
        return False
