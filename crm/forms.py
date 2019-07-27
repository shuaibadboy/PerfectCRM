from django.forms.models import ModelForm
from crm import models


class EnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
        return ModelForm.__new__(cls)

    class Meta:
        model = models.Enrollment
        fields = ['enrolled_class', 'consultant']


class PaymentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
        return ModelForm.__new__(cls)

    def clean_amount(self):
        data = self.cleaned_data['amount']
        if data < 500:
            self.add_error('amount', '最低缴费标准为500元')
        return data

    class Meta:
        model = models.Payment
        fields = '__all__'
        exclude = ['customer', 'course', 'consultant', 'date']


class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'
        return ModelForm.__new__(cls)

    def clean_qq(self):
        data = self.cleaned_data['qq']
        if self.instance.qq != data:
            self.add_error('qq', '别黑我！！！你个臭不要脸！！！')
        return data

    def clean_consult_course(self):
        data = self.cleaned_data['consult_course']
        if self.instance.consult_course != data:
            self.add_error('consult_course', '别黑我！！！你个臭不要脸！！！')
        return data

    def clean_consultant(self):
        data = self.cleaned_data['consultant']
        if self.instance.consultant != data:
            self.add_error('consultant', '别黑我！！！你个臭不要脸！！！')
        return data

    def clean_source(self):
        data = self.cleaned_data['source']
        if self.instance.source != data:
            self.add_error('source', '别黑我！！！你个臭不要脸！！！')
        return data

    class Meta:
        model = models.Customer
        fields = "__all__"
        exclude = ['content', 'status', 'memo', 'tags', 'referral_from']
        readonly_fields = ['qq', 'consult_course', 'consultant', 'source']
