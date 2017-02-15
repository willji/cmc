# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import filters as rffilters
from rest_framework import renderers
from api import models
from api import serializers
import django_filters
import rest_framework_filters as filters


class ApplicationFilter(filters.FilterSet):
    name = django_filters.CharFilter('name')

    class Meta:
        model = models.Application
        fields = ['name',]

class EnvironmentFilter(filters.FilterSet):
    name = django_filters.CharFilter('name')

    class Meta:
        model = models.Environment
        fields = ['name',]

class TemplateTagFilter(filters.FilterSet):
    name = django_filters.CharFilter('name')

    class Meta:
        model = models.TemplateTag
        fields = ['name',]

class TagValueFilter(filters.FilterSet):
    tag = filters.RelatedFilter(TemplateTagFilter, name='tag')
    environment = filters.RelatedFilter(EnvironmentFilter, name='environment')

    class Meta:
        model = models.TagValue

class ApplicationTagFilter(filters.FilterSet):
    application = filters.RelatedFilter(ApplicationFilter, name='application')
    file_path = django_filters.CharFilter('file_path')

    class Meta:
        model = models.ApplicationTag

class PackageFilter(filters.FilterSet):

    application = filters.RelatedFilter(ApplicationFilter, name='application')
    environment = filters.RelatedFilter(EnvironmentFilter, name='environment')

    class Meta:
        model = models.Package

class ApplicationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationSerializer

    # Applies permissions
    permission_classes = (permissions.DjangoModelPermissions, )

    # Applies Filters
    filter_backends = (rffilters.DjangoFilterBackend, rffilters.DjangoObjectPermissionsFilter, )
    filter_fields = ('name',)

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modified_by=self.request.user,
        )
        return super(ApplicationViewSet, self).perform_create(serializer)

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Department.objects.prefetch_related('applications').all()
    serializer_class = serializers.DepartmentSearializer

    # Applies permissions
    permission_classes = (permissions.DjangoModelPermissions,)

    # Applies Filters
    filter_backends = (rffilters.DjangoFilterBackend, rffilters.DjangoObjectPermissionsFilter, )
    filter_fields = ('name',)

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modified_by=self.request.user,
        )
        return super(DepartmentViewSet, self).perform_create(serializer)

class EnvironmentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Environment.objects.all()
    serializer_class = serializers.EnvironmentSerializer

    # Applies permissions
    permission_classes = (permissions.DjangoModelPermissions, )

    # Applies Filters
    filter_backends = (rffilters.DjangoFilterBackend, rffilters.DjangoObjectPermissionsFilter, )
    filter_fields = ('name',)

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modified_by=self.request.user,
        )
        return super(EnvironmentViewSet, self).perform_create(serializer)

class TemplateTagViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.TemplateTag.objects.all()
    serializer_class = serializers.TemplateTagSerializer

    # Applies permissions
    permission_classes = (permissions.DjangoModelPermissions, )

    # Applies Filters
    filter_backends = (rffilters.DjangoFilterBackend, )
    filter_fields = ('name',)

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modified_by=self.request.user,
        )
        return super(TemplateTagViewSet, self).perform_create(serializer)

class ApplicationTagViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.ApplicationTag.objects.select_related('application').prefetch_related('tags').all()
    serializer_class = serializers.ApplicationTagSerializer

    # Applies permissions
    permission_classes = (permissions.DjangoModelPermissions, )

    # Applies Filters
    filter_backends = (rffilters.DjangoFilterBackend, rffilters.DjangoObjectPermissionsFilter, )
    filter_class = ApplicationTagFilter

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modified_by=self.request.user,
        )
        return super(ApplicationTagViewSet, self).perform_create(serializer)

class TagValueViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.TagValue.objects.all()
    serializer_class = serializers.TagValueSerializer

    # Applies permissions
    permission_classes = (permissions.DjangoModelPermissions, )

    # Applies Filters
    filter_backends = (rffilters.DjangoFilterBackend, rffilters.DjangoObjectPermissionsFilter, )
    filter_class = TagValueFilter
    
    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modified_by=self.request.user,
        )
        return super(TagValueViewSet, self).perform_create(serializer)

class PackageViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Package.objects.all()
    serializer_class = serializers.PackageSerializer

    # Applies permissions
    permission_classes = (permissions.DjangoModelPermissions, )

    # Applies Filters
    filter_backends = (rffilters.DjangoFilterBackend, )
    filter_class = PackageFilter    
    
    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modified_by=self.request.user,
        )
        return super(PackageViewSet, self).perform_create(serializer)
