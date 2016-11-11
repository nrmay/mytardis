from django.test import TestCase
from django.contrib.auth.models import User, Group

from tardis.tardis_portal.auth.utils import get_or_create_user
from tardis.tardis_portal.models import UserProfile, UserAuthentication


class GetOrCreateUserTestCase (TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass


    '''
    Test creation of local user
    '''
    def testLocalUser(self):
        method = "localdb"
        user_id = "adminX1"
        email = "admin_x@dummy.edu.au"
        targetedID = None

        (result, created) = get_or_create_user(method, user_id, email)
        assert result is not None
        assert created is True

        profile = UserProfile.objects.get(user=result)
        assert profile is not None
        # assert profile.isDjangoAccount is not None
        # assert profile.isDjangoAccount == True
        assert profile.rapidConnectEduPersonTargetedID is None

        auth = UserAuthentication.objects.get(userProfile=profile)
        assert auth is not None
        print "auth(%s,%s,%s)" % (auth.username,
                                  auth.authenticationMethod,
                                  auth.getAuthMethodDescription)
        assert auth.username == user_id
        assert auth.authenticationMethod is not None
        assert auth.authenticationMethod == method

        return


    '''
    Test creation of CAS user
    '''
    def testCASUser(self):

        return


    '''
    Test creation of AAF user
    '''
    def testAAFUser(self):

        return


    '''
    Test creation of AAFE user
    '''
    def testAAFEUser(self):

        return
