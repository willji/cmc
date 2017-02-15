from django.db import models

# Base models that have some common fields.

class CommonModel(models.Model):
    # Meta data for one object.
    creator = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_creator', verbose_name='creator')
    last_modified_by = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_last_modified_by', verbose_name='last modified by')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class NameModel(models.Model):
    name = models.CharField(max_length=80)

    # Meta data for one object.
    creator = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_creator', verbose_name='creator')
    last_modified_by = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_last_modified_by', verbose_name='last modified by')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

class NameDescModel(models.Model):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)

    # Meta data for one object.
    creator = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_creator', verbose_name='creator')
    last_modified_by = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_last_modified_by', verbose_name='last modified by')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

class UniqueNameDescModel(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    # Meta data for one object.
    creator = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_creator', verbose_name='creator')
    last_modified_by = models.ForeignKey('auth.user', related_name='%(app_label)s_%(class)s_last_modified_by', verbose_name='last modified by')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name