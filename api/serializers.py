# -*- coding: utf-8 -*-

from rest_framework import serializers
from common.serializers import CommonHyperlinkedModelSerializer
from api import models


class ApplicationSerializer(CommonHyperlinkedModelSerializer):
    
    class Meta:
        model = models.Application

class DepartmentSearializer(CommonHyperlinkedModelSerializer):

    applications = serializers.SlugRelatedField(queryset=models.Application.objects.all(), many=True, slug_field='name')

    class Meta:
        model = models.Department

class EnvironmentSerializer(CommonHyperlinkedModelSerializer):

    class Meta:
        model = models.Environment

class TagValueSerializer(CommonHyperlinkedModelSerializer):

    environment = serializers.SlugRelatedField(queryset=models.Environment.objects.all(), slug_field='name')
    tag = serializers.SlugRelatedField(queryset=models.TemplateTag.objects.all(), slug_field='name')

    class Meta:
        model  = models.TagValue

class TemplateTagSerializer(CommonHyperlinkedModelSerializer):

    class Meta:
        model = models.TemplateTag

class ApplicationTagSerializer(CommonHyperlinkedModelSerializer):

    application = serializers.SlugRelatedField(queryset=models.Application.objects.all(), slug_field='name')
    tags = serializers.SlugRelatedField(queryset=models.TemplateTag.objects.all(), many=True, slug_field='name')

    class Meta:
        model = models.ApplicationTag


class PackageSerializer(CommonHyperlinkedModelSerializer):

    application = serializers.SlugRelatedField(queryset=models.Application.objects.all(), slug_field='name')
    environment = serializers.SlugRelatedField(queryset=models.Environment.objects.all(), slug_field='name')

    class Meta:
        model = models.Package