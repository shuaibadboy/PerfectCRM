from django.shortcuts import render, redirect, HttpResponse
from django.db import IntegrityError
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from crm import forms, models
import random, string, os
from PerfectCRM import settings
# Create your views here.


@login_required
def index(request):
    return render(request, 'sales/index.html')


@login_required
def customer_list(request):
    return render(request, 'sales/customers.html')


@login_required
def enrollment(request, customer_id):
    """报名表"""
    customer_obj = models.Customer.objects.get(id=customer_id)
    msg = {}
    enrollment_obj = {}
    if request.method == "POST":
        msg = {'create_status': False}
        customer_form = forms.EnrollmentForm(request.POST)
        if customer_form.is_valid():
            random_str = ''.join(random.sample(string.ascii_lowercase + str(string.digits), 16))
            link = 'http://127.0.0.1:8888/crm/customer/registration/%s/%s/'
            msg['create_status'] = True
            try:
                customer_form.cleaned_data['customer'] = customer_obj
                enrollment_obj = models.Enrollment.objects.create(**customer_form.cleaned_data)
                link = link % (enrollment_obj.id, random_str)
                msg['message'] = '报名信息创建成功，请将报名链接发送给学员：\n <a href="%s">%s</a>' % (link, link)
            except IntegrityError:
                enrollment_obj['enrolled_class'] = request.POST.get('enrolled_class')
                enrollment_obj['customer'] = customer_obj.id
                enrollment_obj = models.Enrollment.objects.get(**enrollment_obj)
                if enrollment_obj.contract_agreed and not enrollment_obj.contract_approved:
                    return redirect('/crm/contract_review/%s/' % enrollment_obj.id)
                consultant_id = request.POST.get('consultant')
                link = link % (enrollment_obj.id, random_str)
                if str(enrollment_obj.consultant.id) != consultant_id:
                    msg['message'] = '该条信息已被其他教员注册，如需继续报名，请将报名链接发送给学员：\n <a href="%s">%s</a>' % (link, link)
                else:
                    msg['message'] = '该条报名信息已被注册，如需继续报名，请将报名链接发送给学员：\n  <a href="%s">%s</a>' % (link, link)
            cache.set(str(enrollment_obj.id), random_str, 6000)
    else:
        customer_form = forms.EnrollmentForm()
    return render(request, 'sales/enrollment.html', {'modelform': customer_form, 'customer_obj': customer_obj,
                                                     'msg': msg, 'enrollment_obj': enrollment_obj})


def stu_registration(request, enrollment_id, random_str):
    """学生上传资料并提交合同"""
    if cache.get(str(enrollment_id)) != random_str:
        return HttpResponse('<h2 style="text-align: center;margin: 50px">页面已过期...</h2>')
    msg = {'status': False, 'message': '报名表已提交！合同正在审核，即将开启您的升华之旅...'}
    enrollment_obj = models.Enrollment.objects.get(id=enrollment_id)
    if request.method == 'POST':
        if request.is_ajax():
            enroll_data_path = os.path.join(settings.ENROLL_DATA, str(enrollment_obj))
            if not os.path.exists(enroll_data_path):
                os.makedirs(enroll_data_path, exist_ok=True)
            for k, file_obj in request.FILES.items():
                file_path = os.path.join(enroll_data_path, file_obj.name)
                with open(file_path, 'wb') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)
            return HttpResponse('上传成功')
        customer_form = forms.CustomerForm(request.POST, instance=enrollment_obj.customer)
        if customer_form.is_valid():
            enrollment_obj.contract_agreed = True
            msg['status'] = True
            enrollment_obj.save()
            customer_form.save()
            return render(request, 'sales/stu_registration.html',
                          {'modelform': customer_form, 'enrollment_obj': enrollment_obj,
                           'msg': msg})
    else:
        if enrollment_obj.contract_agreed:
            msg['status'] = True
            return render(request, 'sales/stu_registration.html', {'enrollment_obj': enrollment_obj, 'msg': msg})
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
    return render(request, 'sales/stu_registration.html', {'modelform': customer_form, 'enrollment_obj': enrollment_obj,
                                                           'msg': msg})


@login_required
def enrollment_rejection(request, enrollment_id):
    """合同填写不符合要求，并驳回合同"""
    enrollment_obj = models.Enrollment.objects.filter(id=enrollment_id)
    enrollment_obj.update(contract_agreed=False)
    return redirect('/crm/customer/%s/enrollment/' % enrollment_obj[0].customer.id)


@login_required
def contract_review(request, enrollment_id):
    """合同审核"""
    enrollment_obj = models.Enrollment.objects.get(id=enrollment_id)
    return render(request, 'sales/contract_review.html', {'enrollment_obj': enrollment_obj})


@login_required
def payment(request, enrollment_id):
    """缴费记录并审核通过合同"""
    enrollment_obj = models.Enrollment.objects.get(id=enrollment_id)
    modelform = forms.PaymentForm()
    if request.method == 'POST':
        modelform = forms.PaymentForm(request.POST)
        if modelform.is_valid():
            amount = int(request.POST.get('amount'))
            # if request.POST.get('customer') != str(enrollment_obj.customer) \
            #         or request.POST.get('course') != str(enrollment_obj.enrolled_class.course) \
            #         or request.POST.get('consultant') != str(enrollment_obj.consultant):
            #     return HttpResponse('别黑我 臭屌丝！！！')
            payment_obj = models.Payment.objects.create(customer=enrollment_obj.customer,
                                                        course=enrollment_obj.enrolled_class.course,
                                                        consultant=enrollment_obj.consultant, amount=amount)
            customer_obj = payment_obj.customer
            enrollment_obj.contract_approved = True
            enrollment_obj.save()
            customer_obj.status = 0
            customer_obj.save()
            return redirect('/crm-admin/crm/customer/')
    return render(request, 'sales/payment.html', {'enrollment_obj': enrollment_obj, 'modelform': modelform})
