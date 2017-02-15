# -*- coding: utf-8 -*-

'''
Definition of views.
'''

import time, logging
from itertools import chain
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.db.models.query_utils import Q
from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import FormMixin
from django.conf import settings
from datetime import datetime
from api import models
from webui import forms
from webui.utilities import ComparisonHelper
from vanilla import ListView, CreateView, UpdateView, DeleteView
from guardian.shortcuts import get_objects_for_group, assign_perm, remove_perm
from django_select2.views import Select2View


#region Regular Views

class IndexView(TemplateView):
    template_name = u'webui/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['title'] = u'主页'

        # content
        context['intro_title'] = u'洋码头配置管理中心'
        context['intro_para'] = u'洋码头配置管理中心用于维护适用于各环境的配置信息，发布系统将使用该系统内的记录生成指定环境中的配置文件。'

        context['imdeveloper'] = u'我是开发人员'
        context['imtest'] = u'我是测试人员'
        context['imops'] = u'我是运维人员'
        
        context['manage'] = u'查看使用教程'
        
        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

class AboutView(TemplateView):

    template_name = u'webui/about.html'

    def get_context_data(self, **kwargs):

        context = super(AboutView, self).get_context_data(**kwargs)

        context['title'] = u'关于'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

class AuthorizationView(TemplateView):

    template_name = u'webui/authorization.html'

    def get_context_data(self, **kwargs):
        context = super(AuthorizationView, self).get_context_data(**kwargs)

        context['title'] = u'正在根据活动目录信息确认权限……'        

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get(self, request, *args, **kwargs):
        try:
            # redirect directly if user is superuser
            if self.request.user.is_superuser:
                return HttpResponseRedirect('/')

            # get OU name from distinguishedName
            ou = self.request.user.ldap_user.dn.split(',')[1].replace('ou=', '').lower()
            knownDeparts = getattr(settings, 'KNOWN_DEPRATMENTS', None)
            groupName = knownDeparts[ou]

            # create group based on known departments if necessary
            django_group = Group.objects.filter(name=groupName)
            if groupName and not django_group:
                Group.objects.create(name=groupName)

            # get group again
            django_group = Group.objects.get(name=groupName)

            # add user to group
            if not django_group.user_set.filter(username=self.request.user.username):
                django_group.user_set.add(self.request.user)

            return HttpResponseRedirect('/')
        except:
            return TemplateResponse(request, 'webui/authorization.html', {
                    'title': '自动授权失败',
                    'introduction': '无法根据活动目录信息确认权限。',
                    'step1': '请确认是否有权限访问配置管理中心获得相关信息。',
                    'step2': '联系运维团队获得授权。',
                    'hello': '欢迎回来, ',
                    'login': '登录',
                    'logout': '注销',
                    'year': datetime.now().year,
                })

class DevHelpView(TemplateView):
    template_name = u'webui/dev_help.html'

    def get_context_data(self, **kwargs):
        context = super(DevHelpView, self).get_context_data(**kwargs)

        context['title'] = u'开发人员使用教程'

        context['introduction_title'] = u'简介'      
        context['introduction_para1'] = u'在洋码头配置管理系统中开发人员负责维护以下信息：'
        context['task1'] = u'应用程序列表。'
        context['task2'] = u'隶属于本部门的应用程序。'
        context['task3'] = u'本部门使用的模板标签。'
        context['task4'] = u'模板标签对应的值。'
        context['task5'] = u'应用配置文件中所关联的模板标签。'

        context['introduction_process'] = u'使用流程'      
        context['introduction_para2'] = u'在使用配置管理中心时，分为两种情况：'
        context['scenario_1'] = u'已存在站点：'
        context['step1_1'] = u'登录 gitlab.ops.ymatou.cn，找到应用所属项目。'
        context['step1_2'] = u'找到需要修改的配置文件，单击编辑按钮。'
        context['step1_3'] = u'按需增加，修改或者删除相应的配置，保存修改。'
        context['step1_4'] = u'登录 cmc.ops.ymatou.cn，单击管理菜单下的配置文件包。'
        context['step1_5'] = u'添加添加，选择需要生成配置文件包的应用名称，环境（仅限测试环境），目标平台。单击提交并等待页面返回。'
        context['step1_6'] = u'如需生成生产环境的配置，请联系运维团队。'
        context['scenario_2'] = u'新站点：'
        context['step2_1'] = u'登录 gitlab.ops.ymatou.cn， 在指定组下创建新的项目。'
        context['step2_2'] = u'修改配置文件，添加模板标签。修改完成后，使用Git客户端将文件提交至线上。'
        context['step2_3'] = u'登录 cmc.ops.ymatou.cn，单击管理菜单下的配置文件包。'
        context['step2_4'] = u'添加添加，选择需要生成配置文件包的应用名称，环境（仅限测试环境），目标平台。单击提交并等待页面返回。'
        context['step2_5'] = u'如需生成生产环境的配置，请联系运维团队。'
        

        context['introduction_security'] = u'权限'
        context['introduction_para3'] = u'在洋码头配置管理系统中，开发人员使用域账号登录后，拥有以下权限：'
        context['secu_perm1'] = u'添加，更新应用程序。查看本部门的应用程序。'
        context['secu_perm2'] = u'更新隶属于本部门的应用程序。'
        context['secu_perm3'] = u'浏览所有模板标签。添加，更新属于本部门的模板标签。'
        context['secu_perm4'] = u'添加，更新，删除本部门维护的模板标签值。浏览非生产环境的模板标签值。'
        context['secu_perm5'] = u'添加，更新，删除配置文件中所使用的模板标签。'

        context['introduction_management'] = u'操作步骤'
        context['introduction_para4'] = u'在洋码头配置管理系统中，开发人员可以按照以下步骤执行相应维护工作：'
        
        context['mgmt_ops01_1'] = u'添加应用程序'
        context['mgmt_ops01_2'] = u'单击管理菜单，单击应用列表。单击左侧的创建按钮，在打开的表单中，输入应用程序名，单击提交。'
        context['mgmt_ops02_1'] = u'更新应用程序'
        context['mgmt_ops02_2'] = u'单击管理菜单，单击应用列表。单击右侧的更新链接，在打开的表单中，更新应用程序名或者描述信息，单击提交。'
        
        context['mgmt_ops03_1'] = u'更新隶属于本部门的应用'
        context['mgmt_ops03_2'] = u'单击管理菜单，单击部门列表。单击右侧的更新链接，在打开的表单中，更新应用程序列表，单击提交。'
        
        context['mgmt_ops04_1'] = u'添加模板标签'
        context['mgmt_ops04_2'] = u'单击管理菜单，单击模板标签。单击左侧的创建按钮，在打开的表单中，输入模板标签名，单击提交。' + \
                                  u'模板表情名必需以 ‘${’ 起始及 ‘}$’ 结束，且仅使用大小写字母，数字及下划线。'
        context['mgmt_ops05_1'] = u'更新模板标签'
        context['mgmt_ops05_2'] = u'单击管理菜单，单击模板标签。单击右侧的更新链接，在打开的表单中，更新模板标签名或者描述信息，单击提交。'

        context['mgmt_ops06_1'] = u'添加模板标签值'
        context['mgmt_ops06_2'] = u'单击管理菜单，单击模板标签值。单击左侧的创建按钮，在打开的表单中，选择需要关联的环境，模板标签及对应的值，单击提交。'
        context['mgmt_ops07_1'] = u'更新模板标签值'
        context['mgmt_ops07_2'] = u'单击管理菜单，单击模板标签值。单击右侧的更新链接，在打开的表单中，更新模板标签值，单击提交。' + \
                                  u'如果关联环境中的模板标签值已存在，则更新失败。'
        context['mgmt_ops08_1'] = u'删除模板标签值'
        context['mgmt_ops08_2'] = u'单击管理菜单，单击模板标签值。单击右侧的删除链接，在打开的表单中，确认删除操作，单击提交。'

        context['mgmt_ops09_1'] = u'添加应用标签'
        context['mgmt_ops09_2'] = u'单击管理菜单，单击应用标签。单击左侧的创建按钮，在打开的表单中，选择需要关联的应用，配置文件相对路径，需要关联的模板标签，单击提交。'
        context['mgmt_ops10_1'] = u'更新应用标签'
        context['mgmt_ops10_2'] = u'单击管理菜单，单击应用标签。单击右侧的更新链接，在打开的表单中，更新配置文件相对路径，需要关联的模板标签，单击提交。' + \
                                  u'如果关联应用中的配置文件相对路径已存在，则更新失败。'
        context['mgmt_ops11_1'] = u'删除应用标签'
        context['mgmt_ops11_2'] = u'单击管理菜单，单击应用标签。单击右侧的删除链接，在打开的表单中，确认删除操作，单击提交。'

        context['mgmt_ops12_1'] = u'添加配置文件打包任务'
        context['mgmt_ops12_2'] = u'单击管理菜单，单击配置文件包。单击左侧的创建按钮，在打开的表单中，选择需要打包配置的应用，环境，目标平台及备注信息（可选），单击提交。'

        context['introduction_package'] = u'配置文件打包任务失败原因及解决方法'
        context['introduction_para5'] = u'在洋码头配置管理系统中，配置文件打包任务可能会因为以下原因引起失败：'
        context['pkg_q_01'] = u'无法在Gitlab中找到相应应用'
        context['pkg_a_01'] = u'确认Gitlab中所属部门下有相应的应用。确认应用被关联到相应部门。'
        context['pkg_q_02'] = u'无法找到与应用程序关联的模板标签'
        context['pkg_a_02'] = u'确认应用程序中使用的模板标签，并将其关联到相关应用。'
        context['pkg_q_03'] = u'无法找到与环境适配的模板值'
        context['pkg_a_03'] = u'确认应用程序中使用的模板标签及模板标签的值，并将标签值关联到对应环境。'
        context['pkg_q_04'] = u'无法打开配置文件'
        context['pkg_a_04'] = u'确认应用标签中的配置文件相对路径是否正确。（路径区分大小写）'
        context['pkg_q_05'] = u'无法在配置文件中找到特定模板标签'
        context['pkg_a_05'] = u'确认配置模板中是否存在该模板标签。确认是否继续使用该模板标签，如果不再使用，则应在应用标签中将该模板标签删除。'
        context['pkg_q_06'] = u'在配置文件中找到未经替换的模板标签'
        context['pkg_a_06'] = u'确认应用标签中，对应的配置文件是否关联了正确数量的模板标签。'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

class TestHelpView(TemplateView):
    template_name = u'webui/test_help.html'

    def get_context_data(self, **kwargs):
        context = super(TestHelpView, self).get_context_data(**kwargs)
        
        context['title'] = u'测试人员使用教程'
        context['introduction_title'] = u'简介'

        context['introduction_para1'] = u'在洋码头配置管理系统中测试人员负责维护以下信息：'
        context['task1'] = u'共同维护公司范围内的应用程序列表。'
        context['task2'] = u'共同维护公司范围内所有部门的应用程序。'
        context['task3'] = u'本部门使用的模板标签。'
        context['task4'] = u'本部门使用的模板标签所对应的值。'
        context['task5'] = u'应用配置文件中所关联的模板标签。'
        context['task6'] = u'配置文件打包'

        context['introduction_security'] = u'权限'
        context['introduction_para2'] = u'在洋码头配置管理系统中，测试人员使用域账号登录后，拥有以下权限：'
        context['secu_perm1'] = u'添加，更新应用程序。查看所有部门的应用程序。'
        context['secu_perm2'] = u'更新所有部门应用程序的隶属关系。'
        context['secu_perm3'] = u'浏览所有模板标签。添加，更新属于本部门的模板标签。'
        context['secu_perm4'] = u'添加，更新，删除本部门维护的模板标签值。浏览非生产环境的模板标签值。'
        context['secu_perm5'] = u'添加，更新，删除配置文件中所使用的模板标签。'

        context['introduction_management'] = u'操作步骤'
        context['introduction_para3'] = u'在洋码头配置管理系统中，测试人员可以按照以下步骤执行相应维护工作：'
        
        context['mgmt_ops01_1'] = u'添加应用程序'
        context['mgmt_ops01_2'] = u'单击管理菜单，单击应用列表。单击左侧的创建按钮，在打开的表单中，输入应用程序名，单击提交。'
        context['mgmt_ops02_1'] = u'更新应用程序'
        context['mgmt_ops02_2'] = u'单击管理菜单，单击应用列表。单击右侧的更新链接，在打开的表单中，更新应用程序名或者描述信息，单击提交。'
        
        context['mgmt_ops03_1'] = u'更新所有部门应用程序的隶属关系。'
        context['mgmt_ops03_2'] = u'单击管理菜单，单击部门列表。单击右侧某一部门的更新链接，在打开的表单中，更新应用程序列表，单击提交。'
        
        context['mgmt_ops04_1'] = u'添加模板标签'
        context['mgmt_ops04_2'] = u'单击管理菜单，单击模板标签。单击左侧的创建按钮，在打开的表单中，输入模板标签名，单击提交。' + \
                                  u'模板表情名必需以 ‘${’ 起始及 ‘}$’ 结束，且仅使用大小写字母，数字及下划线。'
        context['mgmt_ops05_1'] = u'更新模板标签'
        context['mgmt_ops05_2'] = u'单击管理菜单，单击模板标签。单击右侧的更新链接，在打开的表单中，更新模板标签名或者描述信息，单击提交。'

        context['mgmt_ops06_1'] = u'添加模板标签值'
        context['mgmt_ops06_2'] = u'单击管理菜单，单击模板标签值。单击左侧的创建按钮，在打开的表单中，选择需要关联的环境，模板标签及对应的值，单击提交。'
        context['mgmt_ops07_1'] = u'更新模板标签值'
        context['mgmt_ops07_2'] = u'单击管理菜单，单击模板标签值。单击右侧的更新链接，在打开的表单中，更新模板标签值，单击提交。' + \
                                  u'如果关联环境中的模板标签值已存在，则更新失败。'
        context['mgmt_ops08_1'] = u'删除模板标签值'
        context['mgmt_ops08_2'] = u'单击管理菜单，单击模板标签值。单击右侧的删除链接，在打开的表单中，确认删除操作，单击提交。'

        context['mgmt_ops09_1'] = u'添加应用标签'
        context['mgmt_ops09_2'] = u'单击管理菜单，单击应用标签。单击左侧的创建按钮，在打开的表单中，选择需要关联的应用，配置文件相对路径，需要关联的模板标签，单击提交。'
        context['mgmt_ops10_1'] = u'更新应用标签'
        context['mgmt_ops10_2'] = u'单击管理菜单，单击应用标签。单击右侧的更新链接，在打开的表单中，更新配置文件相对路径，需要关联的模板标签，单击提交。' + \
                                  u'如果关联应用中的配置文件相对路径已存在，则更新失败。'
        context['mgmt_ops11_1'] = u'删除应用标签'
        context['mgmt_ops11_2'] = u'单击管理菜单，单击应用标签。单击右侧的删除链接，在打开的表单中，确认删除操作，单击提交。'

        context['mgmt_ops12_1'] = u'添加配置文件打包任务'
        context['mgmt_ops12_2'] = u'单击管理菜单，单击配置文件包。单击左侧的创建按钮，在打开的表单中，选择需要打包配置的应用，环境，目标平台及备注信息（可选），单击提交。'

        context['introduction_package'] = u'配置文件打包任务失败原因及解决方法'
        context['introduction_para4'] = u'在洋码头配置管理系统中，配置文件打包任务可能会因为以下原因引起失败：'
        context['pkg_q_01'] = u'无法在Gitlab中找到相应应用'
        context['pkg_a_01'] = u'确认Gitlab中所属部门下有相应的应用。确认应用被关联到相应部门。'
        context['pkg_q_02'] = u'无法找到与应用程序关联的模板标签'
        context['pkg_a_02'] = u'确认应用程序中使用的模板标签，并将其关联到相关应用。'
        context['pkg_q_03'] = u'无法找到与环境适配的模板值'
        context['pkg_a_03'] = u'确认应用程序中使用的模板标签及模板标签的值，并将标签值关联到对应环境。'
        context['pkg_q_04'] = u'无法打开配置文件'
        context['pkg_a_04'] = u'确认应用标签中的配置文件相对路径是否正确。（路径区分大小写）'
        context['pkg_q_05'] = u'无法在配置文件中找到特定模板标签'
        context['pkg_a_05'] = u'确认配置模板中是否存在该模板标签。确认是否继续使用该模板标签，如果不再使用，则应在应用标签中将该模板标签删除。'
        context['pkg_q_06'] = u'在配置文件中找到未经替换的模板标签'
        context['pkg_a_06'] = u'确认应用标签中，对应的配置文件是否关联了正确数量的模板标签。'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

class OpsHelpView(TemplateView):
    template_name = u'webui/ops_help.html'

    def get_context_data(self, **kwargs):
        context = super(OpsHelpView, self).get_context_data(**kwargs)

        context['title'] = u'运维人员使用教程'
        context['introduction_title'] = u'简介'

        context['introduction_para1'] = u'在洋码头配置管理系统中运维人员负责维护以下信息：'
        context['task1'] = u'共同维护公司范围内的应用程序列表。'
        context['task2'] = u'共同维护公司范围内所有部门的应用程序。'
        context['task3'] = u'本部门使用的模板标签。'
        context['task4'] = u'所有部门使用的模板标签所对应的值。'
        context['task5'] = u'应用配置文件中所关联的模板标签。'
        context['task6'] = u'配置文件打包'

        context['introduction_security'] = u'权限'
        context['introduction_para2'] = u'在洋码头配置管理系统中，运维人员使用域账号登录后，拥有以下权限：'
        context['secu_perm1'] = u'添加，更新应用程序。查看所有部门的应用程序。'
        context['secu_perm2'] = u'更新所有部门应用程序的隶属关系。'
        context['secu_perm3'] = u'浏览所有模板标签。添加，更新属于本部门的模板标签。'
        context['secu_perm4'] = u'添加，更新，删除本部门维护的模板标签值。浏览非生产环境的模板标签值。'
        context['secu_perm5'] = u'添加，更新，删除配置文件中所使用的模板标签。'

        context['introduction_management'] = u'操作步骤'
        context['introduction_para3'] = u'在洋码头配置管理系统中，运维人员可以按照以下步骤执行相应维护工作：'
        
        context['mgmt_ops01_1'] = u'添加应用程序'
        context['mgmt_ops01_2'] = u'单击管理菜单，单击应用列表。单击左侧的创建按钮，在打开的表单中，输入应用程序名，单击提交。'
        context['mgmt_ops02_1'] = u'更新应用程序'
        context['mgmt_ops02_2'] = u'单击管理菜单，单击应用列表。单击右侧的更新链接，在打开的表单中，更新应用程序名或者描述信息，单击提交。'
        
        context['mgmt_ops03_1'] = u'更新所有部门应用程序的隶属关系。'
        context['mgmt_ops03_2'] = u'单击管理菜单，单击部门列表。单击右侧某一部门的更新链接，在打开的表单中，更新应用程序列表，单击提交。'
        
        context['mgmt_ops04_1'] = u'添加模板标签'
        context['mgmt_ops04_2'] = u'单击管理菜单，单击模板标签。单击左侧的创建按钮，在打开的表单中，输入模板标签名，单击提交。' + \
                                  u'模板表情名必需以 ‘${’ 起始及 ‘}$’ 结束，且仅使用大小写字母，数字及下划线。'
        context['mgmt_ops05_1'] = u'更新模板标签'
        context['mgmt_ops05_2'] = u'单击管理菜单，单击模板标签。单击右侧的更新链接，在打开的表单中，更新模板标签名或者描述信息，单击提交。'

        context['mgmt_ops06_1'] = u'添加模板标签值'
        context['mgmt_ops06_2'] = u'单击管理菜单，单击模板标签值。单击左侧的创建按钮，在打开的表单中，选择需要关联的环境，模板标签及对应的值，单击提交。'
        context['mgmt_ops07_1'] = u'更新模板标签值'
        context['mgmt_ops07_2'] = u'单击管理菜单，单击模板标签值。单击右侧的更新链接，在打开的表单中，更新模板标签值，单击提交。' + \
                                  u'如果关联环境中的模板标签值已存在，则更新失败。'
        context['mgmt_ops08_1'] = u'删除模板标签值'
        context['mgmt_ops08_2'] = u'单击管理菜单，单击模板标签值。单击右侧的删除链接，在打开的表单中，确认删除操作，单击提交。'

        context['mgmt_ops09_1'] = u'添加应用标签'
        context['mgmt_ops09_2'] = u'单击管理菜单，单击应用标签。单击左侧的创建按钮，在打开的表单中，选择需要关联的应用，配置文件相对路径，需要关联的模板标签，单击提交。'
        context['mgmt_ops10_1'] = u'更新应用标签'
        context['mgmt_ops10_2'] = u'单击管理菜单，单击应用标签。单击右侧的更新链接，在打开的表单中，更新配置文件相对路径，需要关联的模板标签，单击提交。' + \
                                  u'如果关联应用中的配置文件相对路径已存在，则更新失败。'
        context['mgmt_ops11_1'] = u'删除应用标签'
        context['mgmt_ops11_2'] = u'单击管理菜单，单击应用标签。单击右侧的删除链接，在打开的表单中，确认删除操作，单击提交。'

        context['mgmt_ops12_1'] = u'添加配置文件打包任务'
        context['mgmt_ops12_2'] = u'单击管理菜单，单击配置文件包。单击左侧的创建按钮，在打开的表单中，选择需要打包配置的应用，环境，目标平台及备注信息（可选），单击提交。'

        context['introduction_package'] = u'配置文件打包任务失败原因及解决方法'
        context['introduction_para4'] = u'在洋码头配置管理系统中，配置文件打包任务可能会因为以下原因引起失败：'
        context['pkg_q_01'] = u'无法在Gitlab中找到相应应用'
        context['pkg_a_01'] = u'确认Gitlab中所属部门下有相应的应用。确认应用被关联到相应部门。'
        context['pkg_q_02'] = u'无法找到与应用程序关联的模板标签'
        context['pkg_a_02'] = u'确认应用程序中使用的模板标签，并将其关联到相关应用。'
        context['pkg_q_03'] = u'无法找到与环境适配的模板值'
        context['pkg_a_03'] = u'确认应用程序中使用的模板标签及模板标签的值，并将标签值关联到对应环境。'
        context['pkg_q_04'] = u'无法打开配置文件'
        context['pkg_a_04'] = u'确认应用标签中的配置文件相对路径是否正确。（路径区分大小写）'
        context['pkg_q_05'] = u'无法在配置文件中找到特定模板标签'
        context['pkg_a_05'] = u'确认配置模板中是否存在该模板标签。确认是否继续使用该模板标签，如果不再使用，则应在应用标签中将该模板标签删除。'
        context['pkg_q_06'] = u'在配置文件中找到未经替换的模板标签'
        context['pkg_a_06'] = u'确认应用标签中，对应的配置文件是否关联了正确数量的模板标签。'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

class TemplateTagAppsView(TemplateView):
    template_name = u'api/templatetag_apps.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateTagAppsView, self).get_context_data(**kwargs)
        
        context['title'] = u'模板标签所关联应用'
        context['introduction'] = u'本页面列出了与某一模板标签所关联的应用程序。'
        context['nosuchtag'] = u'无法通过该模板标签ID找到相关应用'
        context['unusedtag'] = u'该模板标签暂未关联任何应用'

        # try to get application tags based on tag id.
        # REF: Related objects reference
        # https://docs.djangoproject.com/en/1.8/ref/models/relations/#related-objects-reference

        try:
            tagid = self.kwargs['pk']
            templatetag = models.TemplateTag.objects.get(pk=tagid)
            context['templatetag'] = templatetag
            context['applicationtags'] = [x for x in templatetag.applicationtag_set.all()]
        except:
            # In case, the url is changed by end user with an incorrect tag id,
            # cfgmgmtcenter should tell end user that something goes wrong.
            context['hasexception'] = True

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

class TemplateTagValueAddView(FormView, Select2View):
    template_name = 'api/template_tag_value_add.html'
    form_class = forms.TemplateTagValueForm
    success_url = reverse_lazy('webui-templatetag-list')

    def get_context_data(self, **kwargs):
        context = super(TemplateTagValueAddView, self).get_context_data(**kwargs)

        context['title'] = u'添加模板标签及值'
        context['introduction'] = u'本页面用于同时添加模板标签及值。'

        context['form'] = self.get_form()

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def form_valid(self, form):
        try:
            tagName = form.cleaned_data['name']
            tagDesc = form.cleaned_data['description'] if True else None
            tagEnvironments = form.cleaned_data['environments']
            tagValue = form.cleaned_data['value']
            
            tagInstance = models.TemplateTag.objects.create(name=tagName, description=tagDesc, creator=self.request.user, last_modified_by=self.request.user)
            tagInstance.save()
            for tagEnvironment in tagEnvironments:
                tagValueInstance = models.TagValue.objects.create(environment=tagEnvironment, tag=tagInstance, value=tagValue, creator=self.request.user, last_modified_by=self.request.user)
                tagValueInstance.save()
        except Exception as e:
            form.add_error(None, e.message)

        return super(TemplateTagValueAddView, self).form_valid(form)

class CopyApplicationTagView(FormView, Select2View):
    template_name = 'api/applicationtag_copy.html'
    form_class = forms.ApplicationTagCopyForm
    success_url = reverse_lazy('webui-applicationtag-list')

    def get_context_data(self, **kwargs):
        context = super(CopyApplicationTagView, self).get_context_data(**kwargs)

        context['title'] = u'复制应用标签'
        context['introduction'] = u'本页面用于为新应用程序快速创建应用标签'

        context['form'] = self.get_form()

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def form_valid(self, form):

        srcApp = form.cleaned_data['source']
        tgtApp = form.cleaned_data['target']
        appTags = models.ApplicationTag.objects.filter(application=srcApp)
        for appTag in appTags:
            newTag = models.ApplicationTag.objects.create(application=tgtApp, file_path=appTag.file_path, 
                                                          creator=self.request.user, last_modified_by=self.request.user)
            newTag.save()
            
            # Permission does not need to be granted here. Because we call save() method. It will trigger post_save signal.

            # Populate template tags.
            for templateTag in appTag.tags.all():
                newTag.tags.add(templateTag)
            newTag.save()

        return super(CopyApplicationTagView, self).form_valid(form)

class MoveApplicationView(FormView, Select2View):
    template_name = 'api/application_move.html'
    form_class = forms.MoveApplicationForm
    success_url = reverse_lazy('webui-department-list')

    # REF: http://stackoverflow.com/questions/8082670/django-user-passes-test-decorator
    # Only ops group or superuser can move application from one department to another
    @method_decorator(user_passes_test(lambda u: u.is_superuser or 'ops' in [x.name for x in u.groups.all()]))
    def dispatch(self, request, *args, **kwargs):
        return super(MoveApplicationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MoveApplicationView, self).get_context_data(**kwargs)

        context['title'] = u'修改应用程序隶属关系'
        context['introduction'] = u'本页面用于为修改应用程序部门隶属关系，包括修改部门应用程序列表，修改应用及应用标签相应对象权限。' + \
                                  u'修改完成后请在Gitlab中确认该应用程序是否进行了相应的修改。'

        context['form'] = self.get_form()

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def form_valid(self, form):

        application = form.cleaned_data['application']
        department = form.cleaned_data['department']

        # move application from original department to target department.
        
        #remove application from original department.
        oldDepartment = application.department_set.first()
        oldDepartment.applications.remove(application)
        oldDepartment.save()
        
        # Add application to target department
        department.applications.add(application)
        department.save()

        # change application object permission.
        # revoke view_application from old group, the grant it to new group.
        oldGroup = Group.objects.get(name=oldDepartment.name)
        newGroup = Group.objects.get(name=department.name)
            
        remove_perm('view_application', oldGroup, application)
        assign_perm('view_application', newGroup, application)

        # change application tags permission.
        appTags = models.ApplicationTag.objects.filter(application=application)
        if appTags:
            for appTag in appTags:
                remove_perm('view_applicationtag', oldGroup, appTag)
                assign_perm('view_applicationtag', newGroup, appTag)

        return super(MoveApplicationView, self).form_valid(form)

#endregion

#region Application Views

class ApplicationListView(ListView):
    model = models.Application
    form_class = forms.SearchForm
    lookup_field = 'name'
    queryset = None
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ApplicationListView, self).get_context_data(**kwargs)

        # add search form
        context['form'] = self.get_form()

        context['title'] = u'应用程序列表'
        
        context['introduction'] = u'本页面列出了所有和部门有关的应用列表，以及模板标签的概览信息。在确认完相关信息后，请在本页面点击生成配置文件夹按钮。'
        context['create'] = u'添加'

        context['update'] = u'更新'
        context['delete'] = u'删除'

        groupNames = [x.name for x in self.request.user.groups.all()]
        if 'ops' in groupNames or 'test' in groupNames:
            context['showcreate'] = False
        else:
            context['showcreate'] = True

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        
        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        if self.request.user.is_superuser:
            if keyword == '':
                return models.Application.objects.select_related('creator', 'last_modified_by').all()
            else:
                return models.Application.objects.select_related('creator', 'last_modified_by').filter(name__icontains=keyword)
        else:
            # REF http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
            # should use list(chain()) here to make sure we don't break other functions.

            results = []
            for group in self.request.user.groups.all():
                if keyword == '':
                    results += get_objects_for_group(group, 'api.view_application', \
                        models.Application.objects.select_related('creator', 'last_modified_by'))
                else:
                    results += get_objects_for_group(group, 'api.view_application', \
                        models.Application.objects.select_related('creator', 'last_modified_by')).filter(name__icontains=keyword)
            return list(chain(results))

class CreateApplicationView(CreateView):
    model = models.Application
    form_class = forms.ApplicationForm
    success_url = reverse_lazy('webui-application-list')

    def get_context_data(self, **kwargs):
        context = super(CreateApplicationView, self).get_context_data(**kwargs)

        context['title'] = u'添加应用程序'
        
        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year   

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['creator'] = self.request.user
        kwargs['last_modified_by'] = self.request.user
        return super(CreateApplicationView, self).get_form(data, files, **kwargs)

class UpdateApplicationView(UpdateView):
    model = models.Application
    form_class = forms.ApplicationForm
    success_url = reverse_lazy('webui-application-list')

    def get_context_data(self, **kwargs):
        context = super(UpdateApplicationView, self).get_context_data(**kwargs)

        context['title'] = u'更新应用程序'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['last_modified_by'] = self.request.user
        return super(UpdateApplicationView, self).get_form(data, files, **kwargs)    

class DeleteApplicationView(DeleteView):
    model = models.Application
    success_url = reverse_lazy('webui-application-list')

    def get_context_data(self, **kwargs):
        context = super(DeleteApplicationView, self).get_context_data(**kwargs)

        context['title'] = u'删除应用'

        context['delete_confirmation'] = u'确实需要删除该应用么？'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

#endregion

#region Department Views

class DepartmentListView(ListView):
    model = models.Department
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(DepartmentListView, self).get_context_data(**kwargs)

        context['title'] = u'部门列表'
        context['introduction'] = u'本页面列出了所有部门信息。'

        context['create'] = u'添加'
        context['update'] = u'更新'
        context['delete'] = u'删除'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Department.objects.select_related('creator', 'last_modified_by').prefetch_related('applications').all()
        else:
            # REF http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
            # should use list(chain()) here to make sure we don't break other functions.
            results = []
            for group in self.request.user.groups.all():
                results += get_objects_for_group(group, 'api.view_department', \
                    models.Department.objects.select_related('creator', 'last_modified_by').prefetch_related('applications'))
            return list(chain(results))

class CreateDepartmentView(CreateView):
    model = models.Department
    form_class = forms.DepartmentForm
    success_url = reverse_lazy('webui-department-list')

    def get_context_data(self, **kwargs):
        context = super(CreateDepartmentView, self).get_context_data(**kwargs)

        context['title'] = u'添加部门'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['creator'] = self.request.user
        kwargs['last_modified_by'] = self.request.user
        return super(CreateDepartmentView, self).get_form(data, files, **kwargs)

class UpdateDepartmentView(UpdateView):
    model = models.Department
    form_class = forms.DepartmentForm
    success_url = reverse_lazy('webui-department-list')

    def get_context_data(self, **kwargs):
        context = super(UpdateDepartmentView, self).get_context_data(**kwargs)

        context['title'] = u'更新部门'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['last_modified_by'] = self.request.user
        return super(UpdateDepartmentView, self).get_form(data, files, **kwargs)

class DeleteDepartmentView(DeleteView):
    model = models.Department
    success_url = reverse_lazy('webui-department-list')

    def get_context_data(self, **kwargs):
        context = super(DeleteDepartmentView, self).get_context_data(**kwargs)

        context['title'] = u'删除部门'      

        context['delete_confirmation'] = u'确实需要删除该部门么？'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

#endregion

#region Environment Views

class EnvironmentListView(ListView):
    model = models.Environment
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(EnvironmentListView, self).get_context_data(**kwargs)

        context['title'] = u'环境名称列表'
        
        context['introduction'] = u'本页面列出了所有和环境名称有关的信息。'
        context['notavailable'] = u'根据目前登录账号，暂无可用信息。'

        context['create'] = u'添加'
        context['update'] = u'更新'
        context['delete'] = u'删除'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Environment.objects.all()
        else:
            # REF http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
            results = []
            for group in self.request.user.groups.all():
                results += get_objects_for_group(group, 'api.view_environment', models.Environment)
            results = chain(results)
            if not results:
                return []
            else:
                return results

class CreateEnvironmentView(CreateView):
    model = models.Environment
    form_class = forms.EnvironmentForm
    success_url = reverse_lazy('webui-environment-list')

    def get_context_data(self, **kwargs):
        context = super(CreateEnvironmentView, self).get_context_data(**kwargs)

        context['title'] = u'添加环境'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        context['errormsg'] = u'环境已存在！'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year       

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['creator'] = self.request.user
        kwargs['last_modified_by'] = self.request.user
        return super(CreateEnvironmentView, self).get_form(data, files, **kwargs)

class UpdateEnvironmentView(UpdateView):
    model = models.Environment
    form_class = forms.EnvironmentForm
    success_url = reverse_lazy('webui-environment-list')

    def get_context_data(self, **kwargs):
        context = super(UpdateEnvironmentView, self).get_context_data(**kwargs)

        context['title'] = u'更新环境信息'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['last_modified_by'] = self.request.user
        return super(UpdateEnvironmentView, self).get_form(data, files, **kwargs)  

class DeleteEnvironmentView(DeleteView):
    model = models.Environment
    success_url = reverse_lazy('webui-environment-list')

    def get_context_data(self, **kwargs):
        context = super(DeleteEnvironmentView, self).get_context_data(**kwargs)

        context['title'] = u'删除环境'

        context['delete_confirmation'] = u'确实需要删除该环境么？'
        
        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

#endregion

#region TemplateTag Views

class TemplateTagListView(ListView):
    model = models.TemplateTag
    form_class = forms.SearchForm
    lookup_field = 'name'
    queryset = None
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(TemplateTagListView, self).get_context_data(**kwargs)

        context['title'] = u'模板标签列表'

        context['introduction'] = u'本页面列出了所有和项目有关的模板标签。'
        context['form'] = self.get_form()

        context['create'] = u'添加'
        context['update'] = u'更新'
        context['delete'] = u'删除'
        context['templatetagapps'] = u'查找相关应用'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):

        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        # all people can view template tag
        if keyword == '':
            return models.TemplateTag.objects.select_related('creator', 'last_modified_by').all()
        else:
            return models.TemplateTag.objects.select_related('creator', 'last_modified_by').filter(name__icontains=keyword)

class CreateTemplateTagView(CreateView):
    model = models.TemplateTag
    form_class = forms.TemplateTagForm
    success_url = reverse_lazy('webui-templatetag-list')

    def get_context_data(self, **kwargs):
        context = super(CreateTemplateTagView, self).get_context_data(**kwargs)

        context['title'] = u'添加模板标签'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year      

        return context

    def get_form(self, data = None, files = None, **kwargs):        
        kwargs['creator'] = self.request.user
        kwargs['last_modified_by'] = self.request.user
        return super(CreateTemplateTagView, self).get_form(data, files, **kwargs)

class UpdateTemplateTagView(UpdateView):
    model = models.TemplateTag
    form_class = forms.TemplateTagForm
    success_url = reverse_lazy('webui-templatetag-list')

    def get_context_data(self, **kwargs):
        context = super(UpdateTemplateTagView, self).get_context_data(**kwargs)

        context['title'] = u'更新模板标签'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['last_modified_by'] = self.request.user
        return super(UpdateTemplateTagView, self).get_form(data, files, **kwargs)

class DeleteTemplateTagView(DeleteView):
    model = models.TemplateTag
    success_url = reverse_lazy('webui-templatetag-list')

    def get_context_data(self, **kwargs):
        context = super(DeleteTemplateTagView, self).get_context_data(**kwargs)

        context['title'] = u'删除模板标签'

        context['delete_confirmation'] = u'确实需要删除该模板标签么？'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

#endregion

#region TagValue Views

class TagValueListView(ListView):
    model = models.TagValue
    form_class = forms.SearchForm
    lookup_field = 'tag__name'
    queryset = None
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(TagValueListView, self).get_context_data(**kwargs)

        context['title'] = u'模板标签值列表'

        context['introduction'] = u'按照你所拥有的权限，本页面列出了所有和项目有关的模板标签值。'
        context['form'] = self.get_form()

        context['create'] = u'添加'
        context['allcreate'] = u'批量添加'
        context['update'] = u'更新'
        context['delete'] = u'删除'

        # login partial
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        queryset = super(TagValueListView, self).get_queryset()\
                   .select_related('environment', 'tag', 'creator', 'last_modified_by')

        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        if self.request.user.is_superuser:
            if keyword == '':
                return queryset
            else:
                return queryset.filter(tag__name__icontains=keyword)
        else:
            # REF http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
            # should use list(chain()) here to make sure we don't break other functions.
            results = []
            for group in self.request.user.groups.all():
                if keyword == '':
                    results += get_objects_for_group(group, 'api.view_tagvalue', queryset)
                else:
                    results += get_objects_for_group(group, 'api.view_tagvalue', queryset.filter(tag__name__icontains=keyword))
            return list(chain(results))

        return queryset

class CreateTagValueView(CreateView):
    model = models.TagValue
    form_class = forms.TagValueForm
    success_url = reverse_lazy('webui-tagvalue-list')

    def get_context_data(self, **kwargs):
        context = super(CreateTagValueView, self).get_context_data(**kwargs)

        context['title'] = u'添加模板标签值'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['creator'] = self.request.user
        kwargs['last_modified_by'] = self.request.user
        return super(CreateTagValueView, self).get_form(data, files, **kwargs)

class AllCreateTagValueView(CreateView):
    model = models.TagValue
    form_class = forms.AllTagValueForm
    success_url = reverse_lazy('webui-tagvalue-list')

    def get_context_data(self, **kwargs):
        context = super(AllCreateTagValueView, self).get_context_data(**kwargs)

        context['title'] = u'批量添加模板标签值'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self,form):
        data = form.data
        environment = models.Environment.objects.get(name='SIT1')
        tag = models.TemplateTag.objects.get(id=int(data.get('tag')))
        value = data.get('value')

        environment1 = models.Environment.objects.get(name='SIT2')
        value1 = data.get('value1')

        environment2 = models.Environment.objects.get(name='UAT')
        value2 = data.get('value2')

        environment3 = models.Environment.objects.get(name='STAGING_PROD')
        value3 = data.get('value3')

        creator = self.request.user
        last_modified_by = self.request.user

        self.model.objects.create(environment=environment,tag=tag,value=value,creator=creator,last_modified_by=last_modified_by)
        self.model.objects.create(environment=environment1,tag=tag,value=value1,creator=creator,last_modified_by=last_modified_by)
        self.model.objects.create(environment=environment2,tag=tag,value=value2,creator=creator,last_modified_by=last_modified_by)
        self.model.objects.create(environment=environment3,tag=tag,value=value3,creator=creator,last_modified_by=last_modified_by)
        return HttpResponseRedirect(self.get_success_url())


class UpdateTagValueView(UpdateView):
    model = models.TagValue
    form_class = forms.TagValueForm
    success_url = reverse_lazy('webui-tagvalue-list')

    def get_context_data(self, **kwargs):
        context = super(UpdateTagValueView, self).get_context_data(**kwargs)

        context['title'] = u'更新模板标签值'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial & commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['last_modified_by'] = self.request.user
        return super(UpdateTagValueView, self).get_form(data, files, **kwargs)

class DeleteTagValueView(DeleteView):
    model = models.TagValue
    success_url = reverse_lazy('webui-tagvalue-list')

    def get_context_data(self, **kwargs):
        context = super(DeleteTagValueView, self).get_context_data(**kwargs)

        context['title'] = u'删除模板标签值'

        context['delete_confirmation'] = u'确实需要删除该模板标签值么？'

        context['btncancel'] = u'取消'
        context['btnsubmit'] = u'提交'

        # login partial
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

#endregion

#region ApplicationTag Views

class ApplicationTagListView(ListView):
    model = models.ApplicationTag
    form_class = forms.SearchForm
    lookup_field = 'application__name'
    queryset = None
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ApplicationTagListView, self).get_context_data(**kwargs)

        context['title'] = u'应用标签列表'
        context['introduction'] = u'本页面列出了所有和项目应用程序关联的模板标签。'

        context['form'] = self.get_form()

        context['create'] = u'添加'
        context['update'] = u'更新'
        context['delete'] = u'删除'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        queryset = super(ApplicationTagListView, self).get_queryset()\
            .select_related('application', 'creator', 'last_modified_by')\
            .prefetch_related('tags')

        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        if self.request.user.is_superuser:
            if keyword == '':
                return queryset
            else:
                return queryset.filter(application__name__icontains=keyword)
        else:
            # REF http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
            # Should use list(chain()) here to make sure we don't break other functions.
            # If one user is member of multiple groups, iterate each group to get objects.
            # Based on the result of django debug toolbar. It's slower after enabling prefetch_related for tags.
            # Using prefetch_related (about 500ms), without using prefetch_related (about 300ms)
            results = []
            for group in self.request.user.groups.all():
                if keyword == '':
                    results += get_objects_for_group(group, 'api.view_applicationtag', queryset)
                else:
                    results += get_objects_for_group(group, 'api.view_applicationtag', queryset.filter(application__name__icontains=keyword))
            return list(chain(results))

class CreateApplicationTagView(CreateView):
    model = models.ApplicationTag
    form_class = forms.ApplicationTagForm
    success_url = reverse_lazy('webui-applicationtag-list')

    def get_context_data(self, **kwargs):
        context = super(CreateApplicationTagView, self).get_context_data(**kwargs)

        context['title'] = u'添加应用标签'      

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year      

        return context

    def get_form(self, data = None, files = None, **kwargs):        
        kwargs['creator'] = self.request.user
        kwargs['last_modified_by'] = self.request.user
        return super(CreateApplicationTagView, self).get_form(data, files, **kwargs)

class UpdateApplicationTagView(UpdateView):
    model = models.ApplicationTag
    form_class = forms.ApplicationTagForm
    success_url = reverse_lazy('webui-applicationtag-list')

    def get_context_data(self, **kwargs):
        context = super(UpdateApplicationTagView, self).get_context_data(**kwargs)

        context['title'] = u'更新应用标签'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['last_modified_by'] = self.request.user
        return super(UpdateApplicationTagView, self).get_form(data, files, **kwargs)

class DeleteApplicationTagView(DeleteView):
    model = models.ApplicationTag
    success_url = reverse_lazy('webui-applicationtag-list')

    def get_context_data(self, **kwargs):
        context = super(DeleteApplicationTagView, self).get_context_data(**kwargs)

        context['title'] = u'删除应用标签'

        context['delete_confirmation'] = u'确实需要删除该应用标签么？'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial and commons
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

#endregion

#region Package Views

class PackageListView(ListView):
    model = models.Package
    form_class = forms.SearchForm
    lookup_field = 'application__name'
    queryset = None
    paginate_by = 15
    
    def get_context_data(self, **kwargs):
        context = super(PackageListView, self).get_context_data(**kwargs)

        context['title'] = u'配置文件包生成记录列表'

        context['introduction'] = u'本页面列出了所有配置包的生成记录， 你也可以在本页面创建新的配置包。' + \
                                  u'测试环境用配置文件包默认会上传至 ftp://cfgpackages.ops.ymt.corp/configuration/<部门名>/<应用>/<环境> 文件夹下。' + \
                                  u'配置文件上传时会同时生成带时间戳的压缩包，以及名为 latest.zip 的压缩包供其它系统调用。'
        context['form'] = self.get_form()

        context['create'] = u'添加'
        context['complete'] = u'完成'
        context['packaging'] = u'正在打包'

        # login partial
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):

        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        if keyword == '':
            return models.Package.objects.select_related('application', 'environment', 'creator', 'last_modified_by')\
                                         .all()
        else:
            return models.Package.objects.select_related('application', 'environment', 'creator', 'last_modified_by')\
                                         .filter(application__name__icontains=keyword)

class CreatePackageView(CreateView):
    model = models.Package
    form_class = forms.PackageForm
    success_url = reverse_lazy('webui-package-list')

    def get_context_data(self, **kwargs):
        context = super(CreatePackageView, self).get_context_data(**kwargs)

        context['title'] = u'配置文件打包'

        context['btnsubmit'] = u'提交'
        context['btncancel'] = u'取消'

        # login partial
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def get_form(self, data = None, files = None, **kwargs):
        kwargs['creator'] = self.request.user
        kwargs['last_modified_by'] = self.request.user
        return super(CreatePackageView, self).get_form(data, files, **kwargs)

class PackageComparisionView(FormView):
    template_name = 'api/package_comparsion.html'
    form_class = forms.ComparisonForm
    success_url = reverse_lazy('webui-package-comparison')
    
    def get_context_data(self, **kwargs):
        context = super(PackageComparisionView, self).get_context_data(**kwargs)

        context['title'] = u'比较配置文件包'
        context['introduction'] = u'本页面用于对已生成的配置文件包进行比较，文件包默认按照生成时间排序。' + \
                                  u'通常只需要选择某一项目的前两个结果进行比较即可。'

        context['btncompare'] = u'比较'
        context['comparisonresult'] = u'比较结果'
        context['hascompared'] = False
        context['identicalpkg'] = u'配置文件包中不存在差异文件。'
        
        context['diffresults'] = None

        # login partial
        context['hello'] = u'欢迎回来, '
        context['login'] = u'登录'
        context['logout'] = u'注销'
        context['year'] = datetime.now().year

        return context

    def form_valid(self, form):
        # REF: 
        # http://stackoverflow.com/questions/6907388/updating-context-data-in-formview-form-valid-method

        try:
            cmpHelper = ComparisonHelper()
            context = self.get_context_data(form=form)

            # Only ops team can compare packages for STAGING_PROD
            groupnames = [x.name for x in self.request.user.groups.all()]
            if form.cleaned_data['srcpackage'].environment.name == settings.PROD_ENV_NAME or \
               form.cleaned_data['destpackage'].environment.name == settings.PROD_ENV_NAME:
                if 'ops' not in groupnames:
                    raise Exception('只有运维团队可以比较生产环境的配置文件包！')

            # Download files
            cmpHelper.download_file(form.cleaned_data['srcpackage'])
            cmpHelper.download_file(form.cleaned_data['destpackage'])

            # Extract files
            cmpHelper.extract_file(form.cleaned_data['srcpackage'])
            cmpHelper.extract_file(form.cleaned_data['destpackage'])

            # Compare files by using filecmp
            # Generate diff by using ghdiff
            diff_results = cmpHelper.compare_file(form.cleaned_data['srcpackage'], form.cleaned_data['destpackage'])
            context['diffresults'] = diff_results

            # Show a tip to indicate that files are identical.
            if not diff_results:
                context['hascompared'] = True

            # Clean files
            cmpHelper.clean_up(form.cleaned_data['srcpackage'])
            cmpHelper.clean_up(form.cleaned_data['destpackage'])

        except Exception as e:
            # REF: http://stackoverflow.com/questions/4229024/django-add-non-field-error-from-view
            form.add_error(None, e.message)

            # We don't need to clean temp files, these files will be replaced in next comparison.
            # If next comparison successes, the temp files will be removed.
            # At least, these files can be removed safely.

        return self.render_to_response(context)

#endregion