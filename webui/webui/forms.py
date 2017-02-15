# -*- coding: utf-8 -*-

'''
Definition of forms.
'''

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.query_utils import Q
from api import models
from webui.utilities import ComparisonHelper
from django_select2 import fields, widgets
from datetime import datetime
import os, re


#region Django Select2 Choices

class ApplicationMultipleChoices(fields.AutoModelSelect2MultipleField):
    queryset = models.Application.objects
    search_fields = ['name__icontains', ]

class ApplicationSingleChoices(fields.AutoModelSelect2Field):
    queryset = models.Application.objects
    search_fields = ['name__icontains',]

class DepartmentSingleChoices(fields.AutoModelSelect2Field):
    queryset = models.Department.objects
    search_fields = ['name__icontains',]

class EnvironmentSingleChoices(fields.AutoModelSelect2Field):
    queryset = models.Environment.objects
    search_fields = ['name__icontains',]

class EnvironmentMultipleChoices(fields.AutoModelSelect2MultipleField):
    queryset = models.Environment.objects
    search_fields = ['name__icontains',]

class TemplateTagSingleChoices(fields.AutoModelSelect2Field):
    queryset = models.TemplateTag.objects
    search_fields = ['name__icontains',]

class TemplateTagMultipleChoices(fields.AutoModelSelect2MultipleField):
    queryset = models.TemplateTag.objects
    search_fields = ['name__icontains',]

class PackageSingleChoices(fields.AutoModelSelect2Field):
    queryset = models.Package.objects
    search_fields = ['name__icontains',]

#endregion

#region Regular Forms

class LoginForm(AuthenticationForm):
    '''Authentication form which uses boostrap CSS.'''
    username = forms.CharField(max_length=255,widget=forms.TextInput({
                                   'class': 'form-control'}))
    password = forms.CharField(label=_('Password'),
                               widget=forms.PasswordInput({
                                   'class': 'form-control'}))

class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=255, widget=forms.TextInput({'class': 'form-control', 'placeholder': '名称'}))

class ComparisonForm(forms.Form):
    srcpackage = PackageSingleChoices(label='文件包一')
    destpackage = PackageSingleChoices(label='文件包二')

    def clean(self):
        # Make sure we are comparing same project with different version.
        if self.data['srcpackage'] and self.data['destpackage']:
            srcPkg = models.Package.objects.get(pk=self.data['srcpackage'])
            destPkg = models.Package.objects.get(pk=self.data['destpackage'])

            if srcPkg == destPkg:
                raise forms.ValidationError('无法比较同一版本的配置文件包！')

            leftProjectName = srcPkg.name.split('_')[0]
            rightProjectName = destPkg.name.split('_')[0]
            if leftProjectName != rightProjectName:
                raise forms.ValidationError('无法比较不同项目的配置文件包！')

    def clean_srcpackage(self):
        data = self.cleaned_data['srcpackage']
        cmpHelper = ComparisonHelper()
        if not cmpHelper.file_exists(data):
            raise forms.ValidationError('服务器上不存在该文件包，无法比较。')
        return data

    def clean_destpackage(self):
        data = self.cleaned_data['destpackage']
        cmpHelper = ComparisonHelper()
        if not cmpHelper.file_exists(data):
            raise forms.ValidationError('服务器上不存在该文件包，无法比较。')
        return data

class TemplateTagValueForm(forms.Form):
    name = forms.CharField(label='模板标签名', max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    description = forms.CharField(label='描述', max_length=255, required=False, widget=forms.TextInput({'class': 'form-control'}))
    environments = EnvironmentMultipleChoices(label='环境')
    value = forms.CharField(label='模板标签值', max_length=1024, widget=forms.TextInput({'class': 'form-control'}))

    def clean_name(self):
        data = self.cleaned_data['name']
        
        if not data.startswith('${') or not data.endswith('}$'):
            raise forms.ValidationError('模板标签名必须以 "${" 开始， 并以 "}$" 结束')
        if len(data) <= 4:
            raise forms.ValidationError('模板标签名不正确')
        trueTagName = data.replace('${', '').replace('}$', '')
        if not re.match('^[a-zA-Z0-9_]+$', trueTagName):
            raise forms.ValidationError('模板标签名仅允许大小写字母，数字，下划线')

        try:
            tag = models.TemplateTag.objects.get(name=data)
            if tag:
                raise forms.ValidationError('模板标签已存在！')
        except:
            pass

        return data

    def clean(self):
        tagName = self.data['name']
        environments= self.cleaned_data['environments']
        for environment in environments:
            filter = Q(environment=environment) & Q(tag__name=tagName)
            if models.TagValue.objects.filter(filter):
                raise forms.ValidationError('{0} 所对应的模板标签值已存在于环境 {1} 中！'.format(tagName, environment.name))

class ApplicationTagCopyForm(forms.Form):
    source = ApplicationSingleChoices(label='源应用程序', required=True)
    target = ApplicationSingleChoices(label='目标应用程序', required=True)

    def clean_source(self):
        data = self.cleaned_data['source']
        appTags = models.ApplicationTag.objects.filter(application=data)

        if not appTags:
            raise forms.ValidationError('{0} 无关联应用标签， 无法进行复制！'.format(data.name))

        return data    

    def clean_target(self):
        data = self.cleaned_data['target']
        appTags = models.ApplicationTag.objects.filter(application=data)

        if appTags:
            raise forms.ValidationError('已有应用标签关联到 {0}， 无法进行复制！'.format(data.name))

        return data

    def clean(self):
        source = self.data['source']
        target = self.data['target']

        if source == target:
            raise forms.ValidationError('源应用程序和目标应用程序相同， 无法进行复制！')

class MoveApplicationForm(forms.Form):
    application = ApplicationSingleChoices(label='应用程序', required=True)
    department = DepartmentSingleChoices(label='所属部门', required=True)

    def clean(self):
        application = self.cleaned_data['application']
        department = self.cleaned_data['department']
        isInDepartment = application.name in [x.name for x in department.applications.all()]

        if isInDepartment:
            raise forms.ValidationError('该应用已关联到 {0}， 无法进行移动！'.format(department.name))

#endregion


#region API forms

class ApplicationForm(forms.ModelForm):

    name = forms.CharField(label='应用程序名', max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    description = forms.CharField(label='描述', required=False, max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        self.last_modified_by = kwargs.pop('last_modified_by', None)
        super(ApplicationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ApplicationForm, self).save(commit=False)
        if self.creator:
            instance.creator = self.creator
        if self.last_modified_by:
            instance.last_modified_by = self.last_modified_by

        return instance.save()

    class Meta:
        model = models.Application
        exclude = ['creator', 'last_modified_by', ]

class DepartmentForm(forms.ModelForm):

    name = forms.CharField(label='部门名', max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    description = forms.CharField(label='描述', required=False, min_length=0, max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    applications = ApplicationMultipleChoices(label='应用列表', required=False)

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        self.last_modified_by = kwargs.pop('last_modified_by', None)
        super(DepartmentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):

        instance = super(DepartmentForm, self).save(commit=False)
        if self.creator:
            instance.creator = self.creator
        if self.last_modified_by:
            instance.last_modified_by = self.last_modified_by
        
        # See the save method in https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/
        # StackOverfolw thread http://stackoverflow.com/questions/28557702/django-form-view-m-to-m-values-not-saved
        # Must call save_m2m()!
        instance.save()
        self.save_m2m()
    
    class Meta:
        model = models.Department
        exclude = ['creator', 'last_modified_by', ]

class EnvironmentForm(forms.ModelForm):
    
    name = forms.CharField(label='环境名', max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    description = forms.CharField(label='描述', required=False, max_length=255, widget=forms.TextInput({'class': 'form-control'}))
       
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        self.last_modified_by = kwargs.pop('last_modified_by', None)
        super(EnvironmentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(EnvironmentForm, self).save(commit=False)
        if self.creator:
            instance.creator = self.creator
        if self.last_modified_by:
            instance.last_modified_by = self.last_modified_by

        return instance.save()

    def clean_name(self):
        data = self.cleaned_data['name']
        if not re.match('^[a-zA-Z0-9_]+$', data):
            raise forms.ValidationError('环境名称仅允许大小写字母，数字，下划线')

        return data

    class Meta:
        model = models.Environment
        exclude = ['creator', 'last_modified_by', ]        

class TemplateTagForm(forms.ModelForm):
    
    name = forms.CharField(label='模板标签名', max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    description = forms.CharField(label='描述', max_length=255, required=False, widget=forms.TextInput({'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        self.last_modified_by = kwargs.pop('last_modified_by', None)
        super(TemplateTagForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(TemplateTagForm, self).save(commit=False)
        if self.creator:
            instance.creator = self.creator
        if self.last_modified_by:
            instance.last_modified_by = self.last_modified_by

        return instance.save()

    def clean_name(self):
        data = self.cleaned_data['name']
        if not data.startswith('${') or not data.endswith('}$'):
            raise forms.ValidationError('模板标签名必须以 "${" 开始， 并以 "}$" 结束')
        if len(data) <= 4:
            raise forms.ValidationError('模板标签名不正确')
        trueTagName = data.replace('${', '').replace('}$', '')
        if not re.match('^[a-zA-Z0-9_]+$', trueTagName):
            raise forms.ValidationError('模板标签名仅允许大小写字母，数字，下划线')

        return data

    class Meta:
        model = models.TemplateTag
        exclude = ['creator', 'last_modified_by', ]

class ApplicationTagForm(forms.ModelForm):
    
    application = ApplicationSingleChoices(label='应用程序')
    file_path = forms.CharField(label='文件相对路径', max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    tags = TemplateTagMultipleChoices(label='模板标签', required=False)
    
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        self.last_modified_by = kwargs.pop('last_modified_by', None)
        super(ApplicationTagForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ApplicationTagForm, self).save(commit=False)
        if self.creator:
            instance.creator = self.creator
        if self.last_modified_by:
            instance.last_modified_by = self.last_modified_by

        # See the save method in https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/
        # StackOverfolw thread http://stackoverflow.com/questions/28557702/django-form-view-m-to-m-values-not-saved
        # Must call save_m2m()!
        instance.save()
        self.save_m2m()

    def clean_file_path(self):
        # Remove white space to make sure we can use the path to find the file later.
        data = self.cleaned_data['file_path'].strip()
        if not data.startswith('/'):
            raise forms.ValidationError('文件路径必须使用以 / 开始的相对路径')

        return data
        
    class Meta:
        model = models.ApplicationTag
        exclude = ['creator', 'last_modified_by', ]

class TagValueForm(forms.ModelForm):
    
    environment = EnvironmentSingleChoices(label='关联环境')
    tag = TemplateTagSingleChoices(label='模板标签')
    value = forms.CharField(label='值', max_length=1024, widget=forms.TextInput({'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        self.last_modified_by = kwargs.pop('last_modified_by', None)
        super(TagValueForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(TagValueForm, self).save(commit=False)
        if self.creator:
            instance.creator = self.creator
        if self.last_modified_by:
            instance.last_modified_by = self.last_modified_by

        return instance.save()

    class Meta:
        model = models.TagValue
        exclude = ['creator', 'last_modified_by', ]

class PackageForm(forms.ModelForm):

    application = ApplicationSingleChoices(label='应用')
    environment = EnvironmentSingleChoices(label='环境')
    branch_name = forms.CharField(label='GITLAB分支名称(区分大小写)', max_length=255, required=False, widget=forms.TextInput({'class': 'form-control'}))
    target_platform = forms.ChoiceField(choices=models.Package.platforms, label='目标平台', widget=forms.Select({'class': 'form-control'}))
    description = forms.CharField(label='备注信息', max_length=255, required=False, widget=forms.TextInput({'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.creator = kwargs.pop('creator', None)
        self.last_modified_by = kwargs.pop('last_modified_by', None)
        super(PackageForm, self).__init__(*args, **kwargs)

    def clean_environment(self):
        groupnames = [x.name for x in self.creator.groups.all()]
        if self.cleaned_data['environment'].name == settings.PROD_ENV_NAME:
            if 'ops' not in groupnames:
                raise forms.ValidationError('只有运维团队可以打包生产环境的配置文件包！')
        return self.cleaned_data['environment']

    def save(self, commit=True):
        instance = super(PackageForm, self).save(commit=False)

        departmentName = None
        for department in models.Department.objects.all():
            if instance.application in department.applications.all():
                departmentName = department.name
                break

        if self.creator:
            instance.creator = self.creator
        if self.last_modified_by:
            instance.last_modified_by = self.last_modified_by
        instance.name = '{0}_{1}'.format(instance.application.name, datetime.now().strftime('%Y%m%d%H%M%S'))

        if instance.environment.name == settings.PROD_ENV_NAME:
            instance.output_path = 'ftp://{0}/{1}/{2}/{3}/{4}'.format(settings.FTP_PROD_SERVER, 'configuration', departmentName, instance.application.name, instance.environment.name)
        else:
            instance.output_path = 'ftp://{0}/{1}/{2}/{3}/{4}'.format(settings.FTP_TEST_SERVER, 'configuration', departmentName, instance.application.name, instance.environment.name)

        # status will be changed later.
        instance.status = None

        return instance.save()

    class Meta:
        model = models.Package
        exclude = ['name', 'creator', 'last_modified_by', 'output_path', 'status']

#endregion