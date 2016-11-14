from django.test import TestCase
import logging

from django.contrib.auth.models import User, Group

from tardis.tardis_portal.auth.utils import get_or_create_user
from tardis.tardis_portal.models import UserProfile, UserAuthentication
from tardis.tardis_portal.views.authentication import cas_callback

logger = logging.getLogger(__name__)

class GetOrCreateUserTestCase (TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    '''
    Verify that a user is well formed.
    '''
    def verifyUser(self, auth_method, user_id):

        # verify User
        userX = User.objects.get(username=user_id)
        assert userX is not None
        assert userX.username is not None
        assert userX.username == user_id
        logger.debug("User object is valid!")

        # verify UserProfile
        profile = UserProfile.objects.get(user=userX)
        assert profile is not None
        assert profile.isDjangoAccount is not None
        assert profile.isDjangoAccount is False
        assert profile.rapidConnectEduPersonTargetedID is None
        logger.debug("UserProfile object is valid!")

        # verify UserAuthentication
        auth = UserAuthentication.objects.get(userProfile=profile)
        assert auth is not None
        logger.debug("auth(%s,%s,%s)" % (auth.username,
                                  auth.authenticationMethod,
                                  auth.getAuthMethodDescription))
        assert auth.username == user_id
        assert auth.authenticationMethod is not None
        assert auth.authenticationMethod == auth_method
        logger.debug("UserAuthentication object is valid!")

        return True


    '''
    Test creation of local user
    '''
    def testLocalUser(self):
        method = "localdb"
        user_id = "adminX1"
        email = "admin_x@dummy.edu.au"
        targetedID = None

        # create user
        (result, created) = get_or_create_user(method, user_id, email)
        assert result is not None
        assert created is True
        assert self.verifyUser(method,user_id) is True

        return


    '''
    Test creation of CAS user
    '''
    def testCASUser(self):
        method = 'cas'
        user_id = 'casUser1'

        # create user
        cas_callback({'user': user_id})
        assert self.verifyUser(method, user_id)

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
