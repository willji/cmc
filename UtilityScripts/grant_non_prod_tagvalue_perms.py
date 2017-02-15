# Running following script in <manage.py shell>

from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm
from api.models import TagValue

# get test group
testGroup, created = Group.objects.get_or_create(name='test')

# get existing non-prod tag value instances
instances = TagValue.objects.exclude(environment__name='STAGING_PROD')

# assign change_tagvalue to test team.
for instance in instances:
    assign_perm('change_tagvalue', testGroup, instance)