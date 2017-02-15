from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    # REF: http://stackoverflow.com/questions/8000022/django-template-how-to-lookup-a-dictionary-value-with-a-variable
    # Usage: handling errors in templates

    return dictionary.get(key)

@register.filter
def is_groupmember(user, groupname):
    # REF: https://docs.djangoproject.com/en/1.9/howto/custom-template-tags/#writing-custom-template-filters
    # Usage: check user's member, it's used in layout.html.
    groupNames = [x.name for x in user.groups.all()]
    isGroupMember = groupname in groupNames
    return isGroupMember