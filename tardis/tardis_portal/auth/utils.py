'''
Created on 15/03/2011

@author: gerson
'''
import logging

from django.conf import settings
from django.contrib.auth.models import User, Group
from tardis.tardis_portal.models import UserProfile, UserAuthentication

logger = logging.getLogger(__name__)


def get_or_create_user(auth_method, user_id, email='', targetedID=''):
    """ Get a User, or Create a User if one does not exist for this
    combination of auth_method and user_id.
    :param auth_method: the authentication method: 'aaf', 'cas', 'localdb'.
    :param user_id: the user identifier for this user.
    :param email: the user's email address.
    :param targetedID: the unique key for this user returned by AAF.
    """
    logger.debug('start!')
    try:
        # check if the given username in combination with the
        # auth method is already in the UserAuthentication table
        user = UserAuthentication.objects.get(username=user_id,
            authenticationMethod=auth_method).userProfile.user
        created = False
        logger.debug('user(%s,%s) found!' % (auth_method, user_id))

    except UserAuthentication.DoesNotExist:
        logger.debug('UserAuthentication.DoesNotExist... creating user!')
        user = create_user(auth_method, user_id, email, targetedID)
        created = True
        logger.debug('user(%s,%s) created!' % (auth_method, user_id))

    return (user, created)


def create_user(auth_method, user_id, email='', targetedID=''):
    """ Create a User for this combination of auth_method and user_id.
    :param auth_method: the authentication method: 'aaf', 'cas', 'localdb'.
    :param user_id: the user identifier for this user.
    :param email: the user's email address.
    :param targetedID: the unique key for this user returned by AAF.
    """
    logger.debug('start!')
    # length of the maximum username
    max_length = 254

    # the username to be used on the User table
    unique_username = user_id[:max_length]
    username_prefix = unique_username

    # Generate a unique username
    i = 0
    try:
        while (User.objects.get(username=unique_username)):
            i += 1
            unique_username = username_prefix[
                :max_length - len(str(i))] + str(i)
    except User.DoesNotExist:
        logger.debug('User.DoesNotExists!')

    password = User.objects.make_random_password()

    # create object: User
    user = User.objects.create_user(username=unique_username,
                                    password=password,
                                    email=email)

    for group_name in settings.NEW_USER_INITIAL_GROUPS:
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            pass
    user.save()
    logger.debug('user created!')

    # update object: UserProfile
    user.userprofile.isDjangoAccount = False
    if auth_method == 'localdb':
        user.userprofile.isDjangoAccount = True
    user.userprofile.rapidConnectEduPersonTargetedID = None
    if targetedID:
        user.userprofile.rapidConnectEduPersonTargetedID = targetedID
    user.userprofile.save()
    logger.debug('userProfile created!')

    # create object: UserAuthentication
    userAuth = UserAuthentication(username=user_id,
                                  userProfile=user.userprofile,
                                  authenticationMethod=auth_method)
    userAuth.save()
    logger.debug('userAuthentication created!')

    return user


def configure_user(user):
    """ Configure a user account that has just been created by adding
    the user to the default groups and creating a UserProfile.

    :param user: the User instance for the newly created account
    """
    for group_name in settings.NEW_USER_INITIAL_GROUPS:
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            pass
    user.userprofile.isDjangoAccount = False
    user.userprofile.save()
    return user.userprofile
