from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg, Max, Min, Sum

register = template.Library()   # register的名字是固定的,不可改变


@register.simple_tag
def course_schedule(enrollment_obj):
    """返回课程进度"""
    return enrollment_obj.enrolled_class.courserecord_set.filter(from_class=enrollment_obj.enrolled_class).count()


@register.simple_tag
def my_course_score(enrollment_obj):
    """返回课程进度"""
    score = 0
    course_record_objs = enrollment_obj.enrolled_class.courserecord_set.filter(from_class=enrollment_obj.enrolled_class)
    for course_record_obj in course_record_objs:
        score += course_record_obj.studyrecord_set.filter(student=enrollment_obj).aggregate(Sum('score'))['score__sum']
    return score


@register.simple_tag
def return_attendance(studyrecord_obj):
    """返回签到详情"""
    return studyrecord_obj.attendance_choice[studyrecord_obj.attendance][1]
