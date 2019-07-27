from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from crm import models
import os, time, json
from PerfectCRM import settings
# Create your views here.


@login_required
def index(request):
    """返回学生首页"""
    return render(request, 'students/my_classes.html')


@login_required
def studyrecord(request, class_id):
    """返回学习记录"""
    enrollment_obj = models.Enrollment.objects.filter(customer=request.user.stu_account, enrolled_class=class_id)
    courserecord_obj = models.CourseRecord.objects.filter(from_class=class_id)
    studyrecord_objs = models.StudyRecord.objects.filter(student__in=enrollment_obj, course_record__in=courserecord_obj)
    return render(request, 'students/studyrecord.html', {'studyrecord_objs': studyrecord_objs,
                                                         'enrollment_obj': enrollment_obj})


@login_required
def homework_detail(request, studyrecord_id):
    """返回学习记录的作业详情"""
    file_list = []
    studyrecord_obj = models.StudyRecord.objects.get(id=studyrecord_id)
    homework_data_path = os.path.join(settings.HOMEWORK_DATA,
                                      str(studyrecord_obj.course_record.from_class.id),
                                      str(studyrecord_obj.course_record.id),
                                      str(studyrecord_obj.id))
    if request.method == 'POST':
        if request.is_ajax():
            if not os.path.exists(homework_data_path):
                os.makedirs(homework_data_path, exist_ok=True)
            for k, file_obj in request.FILES.items():
                file_path = os.path.join(homework_data_path, file_obj.name)
                with open(file_path, 'wb') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)
            for file_name in os.listdir(homework_data_path):
                f_path = os.path.join(homework_data_path, file_name)
                file_create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getatime(f_path)))
                file_size = round(os.path.getsize(f_path)/float(1024*1024), 2)
                file_list.append({
                    'file_name': file_name,
                    'file_size': file_size,
                    'file_create_time': file_create_time
                })
            return HttpResponse(json.dumps({'status': 0, 'msg': 'success', 'file_list': file_list}))
    if os.path.exists(homework_data_path):
        for file_name in os.listdir(homework_data_path):
            f_path = os.path.join(homework_data_path, file_name)
            file_create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getatime(f_path)))
            file_size = round(os.path.getsize(f_path)/float(1024*1024), 2)
            file_list.append({
                'file_name': file_name,
                'file_size': file_size,
                'file_create_time': file_create_time
            })
    return render(request, 'students/homework_detail.html', {'studyrecord_obj': studyrecord_obj, 'file_list': file_list})
