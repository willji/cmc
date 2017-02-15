# -*- coding: utf-8 -*-

"""
Definition of urls for webui.
"""

from datetime import datetime
from django.conf.urls import patterns, url, include
from webui import views
from webui.forms import LoginForm
from django.contrib.auth.decorators import login_required, permission_required


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^authorization/$', login_required(views.AuthorizationView.as_view()), name='authorization'),
    url(r'^devhelp/$', login_required(views.DevHelpView.as_view()), name='devhelp'),
    url(r'^testhelp/$', login_required(views.TestHelpView.as_view()), name='testhelp'),
    url(r'^opshelp/$', login_required(views.OpsHelpView.as_view()), name='opshelp'),
    url(r'^templatetagapps/(?P<pk>\d+)/$', login_required(views.TemplateTagAppsView.as_view()), name='templatetagapps'),
    url(r'^addtemplatetagvalues/$', login_required(views.TemplateTagValueAddView.as_view()), name='addtemplatetagvalues'),
    url(r'^copyapplicationtags/$', login_required(views.CopyApplicationTagView.as_view()), name='copyapplicationtags'),
    url(r'^moveapplication/$', login_required(views.MoveApplicationView.as_view()), name='moveapplication'),
    
    # Application
    url(r'^applications/$', login_required(views.ApplicationListView.as_view()), name='webui-application-list'),
    url(r'^applications/create/$', login_required(views.CreateApplicationView.as_view()), name='webui-application-create'),
    url(r'^applications/update/(?P<pk>\d+)/$', login_required(views.UpdateApplicationView.as_view()), name='webui-application-update'),
    url(r'^applications/delete/(?P<pk>\d+)/$', login_required(views.DeleteApplicationView.as_view()), name='webui-application-delete'),

    # Department    
    url(r'^departments/$', login_required(views.DepartmentListView.as_view()), name='webui-department-list'),
    url(r'^departments/create/$', permission_required('api.add_department')(views.CreateDepartmentView.as_view()), name='webui-department-create'),
    url(r'^departments/update/(?P<pk>\d+)/$', permission_required('api.change_department')(views.UpdateDepartmentView.as_view()), name='webui-department-update'),
    url(r'^departments/delete/(?P<pk>\d+)/$', permission_required('api.delete_department')(views.DeleteDepartmentView.as_view()), name='webui-department-delete'),

    # Environment    
    url(r'^environments/$', login_required(views.EnvironmentListView.as_view()), name='webui-environment-list'),
    url(r'^environments/create/$', permission_required('api.add_environment')(views.CreateEnvironmentView.as_view()), name='webui-environment-create'),
    url(r'^environments/update/(?P<pk>\d+)/$', permission_required('api.change_environment')(views.UpdateEnvironmentView.as_view()), name='webui-environment-update'),
    url(r'^environments/delete/(?P<pk>\d+)/$', permission_required('api.delete_environment')(views.DeleteEnvironmentView.as_view()), name='webui-environment-delete'),

    # TemplateTag
    url(r'^templatetags/$', login_required(views.TemplateTagListView.as_view()), name='webui-templatetag-list'),
    url(r'^templatetags/create/$', permission_required('api.add_templatetag')(views.CreateTemplateTagView.as_view()), name='webui-templatetag-create'),
    url(r'^templatetags/update/(?P<pk>\d+)/$', permission_required('api.change_templatetag')(views.UpdateTemplateTagView.as_view()), name='webui-templatetag-update'),
    url(r'^templatetags/delete/(?P<pk>\d+)/$', permission_required('api.delete_templatetag')(views.DeleteTemplateTagView.as_view()), name='webui-templatetag-delete'),

    # ApplicationTag    
    url(r'^applicationtags/$', login_required(views.ApplicationTagListView.as_view()), name='webui-applicationtag-list'),
    url(r'^applicationtags/create/$', permission_required('api.add_applicationtag')(views.CreateApplicationTagView.as_view()), name='webui-applicationtag-create'),
    url(r'^applicationtags/update/(?P<pk>\d+)/$', permission_required('api.change_applicationtag')(views.UpdateApplicationTagView.as_view()), name='webui-applicationtag-update'),
    url(r'^applicationtags/delete/(?P<pk>\d+)/$', permission_required('api.delete_applicationtag')(views.DeleteApplicationTagView.as_view()), name='webui-applicationtag-delete'),

    # TagValue    
    url(r'^tagvalues/$', login_required(views.TagValueListView.as_view()), name='webui-tagvalue-list'),
    url(r'^tagvalues/create/$', permission_required('api.add_tagvalue')(views.CreateTagValueView.as_view()), name='webui-tagvalue-create'),
    url(r'^tagvalues/allcreate/$', permission_required('api.add_tagvalue')(views.AllCreateTagValueView.as_view()), name='webui-tagvalue-all-create'),
    url(r'^tagvalues/update/(?P<pk>\d+)/$', permission_required('api.change_tagvalue')(views.UpdateTagValueView.as_view()), name='webui-tagvalue-update'),
    url(r'^tagvalues/delete/(?P<pk>\d+)/$', permission_required('api.delete_tagvalue')(views.DeleteTagValueView.as_view()), name='webui-tagvalue-delete'),

    # Package    
    url(r'^packages/$', login_required(views.PackageListView.as_view()), name='webui-package-list'),
    url(r'^packages/create/$', login_required(views.CreatePackageView.as_view()), name='webui-package-create'),
    url(r'^packages/comparison/$', login_required(views.PackageComparisionView.as_view()), name='webui-package-comparison'),
    
    # Django Select2
    url(r'^select2/', include('django_select2.urls')),

    # Login & Logout
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {
            'template_name': 'webui/login.html',
            'authentication_form': LoginForm,
            'extra_context':
            {
                'title':'登录',
                'helpmsg':'请使用域账号登录',
                'username':'用户名',
                'hello':'欢迎回来',
                'login':'登录',
                'logout':'注销',
                'password':'密码',
                'wrongcred':'请输入正确的用户名和密码',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        'django.contrib.auth.views.logout',
        {
            'next_page': '/',
        },
        name='logout'),
)