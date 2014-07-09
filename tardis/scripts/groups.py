#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file has been automatically generated.
# Instead of changing it, create a file called import_helper.py
# which this script has hooks to.
#
# On that file, don't forget to add the necessary Django imports
# and take a look at how locate_object() and save_or_locate()
# are implemented here and expected to behave.
#
# This file was generated with the following command:
# bin/django dumpscript auth.group
#
# to restore it, run
# manage.py runscript module_name.this_script_name
#
# example: if manage.py is at ./manage.py
# and the script is at ./some_folder/some_script.py
# you must make sure ./some_folder/__init__.py exists
# and run  ./manage.py runscript some_folder.some_script


IMPORT_HELPER_AVAILABLE = False
try:
    import import_helper
    IMPORT_HELPER_AVAILABLE = True
except ImportError:
    pass

import datetime
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

def run():
    #initial imports
    from django.contrib.auth.models import Permission
    from django.contrib.auth.models import Group
    from django.contrib.auth.models import User
    from tardis.tardis_portal.models.access_control import GroupAdmin
     
    def locate_object(original_class, original_pk_name, the_class, pk_name, pk_value, obj_content):
        if IMPORT_HELPER_AVAILABLE and hasattr(import_helper, "locate_object"):
            return import_helper.locate_object(original_class, original_pk_name, the_class, pk_name, pk_value, obj_content)
        search_data = { pk_name: pk_value }
        the_obj = the_class.objects.get(**search_data)
        return the_obj

    def save_or_locate(the_obj):
        if IMPORT_HELPER_AVAILABLE and hasattr(import_helper, "save_or_locate"):
            the_obj = import_helper.save_or_locate(the_obj)
        else:
            the_obj.save()
        return the_obj

    # locate superuser
    root_user = locate_object(User, "username", User, "username", u'root', {} )

    # Processing model: Group
    try:
        auth_group_1 = locate_object(Group, "name", Group, "name", u'Administrators', {})
        print("group name[Administrators] skipped: already exists!")
    except:
        # create group
        auth_group_1 = Group()
        auth_group_1.name = u'Administrators'
        auth_group_1 = save_or_locate(auth_group_1)
        # add permissions
        auth_group_1.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'add_user', {} )  )
        auth_group_1.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'change_user', {} )  )
        # add group admin
        group_admin_1 = GroupAdmin()
        group_admin_1.user = root_user
        group_admin_1.group =  auth_group_1
        group_admin_1 = save_or_locate(group_admin_1)

    try: 
        auth_group_2 = locate_object(Group, "name", Group, "name", u'Users', {})
        print("group name[Users] skipped: already exists!")
    except:
        # create group
        auth_group_2 = Group()
        auth_group_2.name = u'Users'
        auth_group_2 = save_or_locate(auth_group_2)
        # add Permissions
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'add_group', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'change_group', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'add_dataset', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'change_dataset', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'add_dataset_file', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'add_experiment', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'change_experiment', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'add_groupadmin', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'change_groupadmin', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'change_objectacl', {} )  )
        auth_group_2.permissions.add(  locate_object(Permission, "codename", Permission, "codename", u'change_userauthentication', {} )  )
        # add group admin
        group_admin_2 = GroupAdmin()
        group_admin_2.user = root_user
        group_admin_2.group =  auth_group_2
        group_admin_2 = save_or_locate(group_admin_2)
        
# end of script #
