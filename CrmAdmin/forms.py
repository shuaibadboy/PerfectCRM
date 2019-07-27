from django.forms import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _
from django import forms
from CrmAdmin .crmadmin import enabled_admins


def create_model_forms(admin_class, form_add=False):
    """
    动态生成ModelForm
    form_add默认为False表单添加只读字段，为True时取消只读字段；
    """
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            try:
                if field_obj.widget.input_type == 'checkbox':
                    field_obj.widget.attrs['class'] = 'checkbox'
            except AttributeError:
                pass
            if not form_add:
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'
        return ModelForm.__new__(cls)

    def default_clean(self):
        """form default clean method"""
        app_name = self.Meta.model._meta.app_label
        model_name = self.Meta.model._meta.model_name
        admin_class = enabled_admins[app_name][model_name]
        if admin_class.readonly_table is True:
            raise forms.ValidationError(_("This is a readonly table!"))

    class Meta:
        model = admin_class.model
        fields = '__all__'
        exclude = admin_class.modelform_exclude_fields

    models_class = admin_class.model
    model_name = '%sModelForm' % models_class._meta.model_name
    func_dir = {'Meta': Meta}
    _model_form_class = type(model_name, (ModelForm,), func_dir)
    setattr(_model_form_class, '__new__', __new__)
    setattr(_model_form_class, 'clean', default_clean)
    return _model_form_class
