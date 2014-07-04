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

    def locate_object(original_class, original_pk_name, the_class, pk_name, pk_value, obj_content):
        #You may change this function to do specific lookup for specific objects
        #
        #original_class class of the django orm's object that needs to be located
        #original_pk_name the primary key of original_class
        #the_class      parent class of original_class which contains obj_content
        #pk_name        the primary key of original_class
        #pk_value       value of the primary_key
        #obj_content    content of the object which was not exported.
        #
        #you should use obj_content to locate the object on the target db
        #
        #and example where original_class and the_class are different is
        #when original_class is Farmer and
        #the_class is Person. The table may refer to a Farmer but you will actually
        #need to locate Person in order to instantiate that Farmer
        #
        #example:
        #if the_class == SurveyResultFormat or the_class == SurveyType or the_class == SurveyState:
        #    pk_name="name"
        #    pk_value=obj_content[pk_name]
        #if the_class == StaffGroup:
        #    pk_value=8


        if IMPORT_HELPER_AVAILABLE and hasattr(import_helper, "locate_object"):
            return import_helper.locate_object(original_class, original_pk_name, the_class, pk_name, pk_value, obj_content)

        search_data = { pk_name: pk_value }
        the_obj =the_class.objects.get(**search_data)
        return the_obj

    def save_or_locate(the_obj):
        if IMPORT_HELPER_AVAILABLE and hasattr(import_helper, "save_or_locate"):
            the_obj = import_helper.save_or_locate(the_obj)
        else:
            the_obj.save()
        return the_obj



    #Processing model: Group

    from django.contrib.auth.models import Group

    auth_group_1 = Group()
    auth_group_1.name = u'Administrators'
    auth_group_1 = save_or_locate(auth_group_1)

    auth_group_2 = Group()
    auth_group_2.name = u'My Group'
    auth_group_2 = save_or_locate(auth_group_2)

    auth_group_3 = Group()
    auth_group_3.name = u'test'
    auth_group_3 = save_or_locate(auth_group_3)

    auth_group_4 = Group()
    auth_group_4.name = u'Users'
    auth_group_4 = save_or_locate(auth_group_4)

    #Re-processing model: Group

    auth_group_1.permissions.add(  locate_object(Permission, "id", Permission, "id", 4, {'codename': u'add_group', 'content_type_id': 2L, 'name': u'Can add group', 'id': 4L} )  )
    auth_group_1.permissions.add(  locate_object(Permission, "id", Permission, "id", 5, {'codename': u'change_group', 'content_type_id': 2L, 'name': u'Can change group', 'id': 5L} )  )
    auth_group_1.permissions.add(  locate_object(Permission, "id", Permission, "id", 7, {'codename': u'add_user', 'content_type_id': 3L, 'name': u'Can add user', 'id': 7L} )  )
    auth_group_1.permissions.add(  locate_object(Permission, "id", Permission, "id", 8, {'codename': u'change_user', 'content_type_id': 3L, 'name': u'Can change user', 'id': 8L} )  )



    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 4, {'codename': u'add_group', 'content_type_id': 2L, 'name': u'Can add group', 'id': 4L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 5, {'codename': u'change_group', 'content_type_id': 2L, 'name': u'Can change group', 'id': 5L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 49, {'codename': u'add_dataset', 'content_type_id': 17L, 'name': u'Can add dataset', 'id': 49L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 50, {'codename': u'change_dataset', 'content_type_id': 17L, 'name': u'Can change dataset', 'id': 50L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 61, {'codename': u'add_dataset_file', 'content_type_id': 21L, 'name': u'Can add dataset_ file', 'id': 61L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 43, {'codename': u'add_experiment', 'content_type_id': 15L, 'name': u'Can add experiment', 'id': 43L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 44, {'codename': u'change_experiment', 'content_type_id': 15L, 'name': u'Can change experiment', 'id': 44L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 31, {'codename': u'add_groupadmin', 'content_type_id': 11L, 'name': u'Can add group admin', 'id': 31L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 32, {'codename': u'change_groupadmin', 'content_type_id': 11L, 'name': u'Can change group admin', 'id': 32L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 38, {'codename': u'change_objectacl', 'content_type_id': 13L, 'name': u'Can change object acl', 'id': 38L} )  )
    auth_group_4.permissions.add(  locate_object(Permission, "id", Permission, "id", 35, {'codename': u'change_userauthentication', 'content_type_id': 12L, 'name': u'Can change user authentication', 'id': 35L} )  )

