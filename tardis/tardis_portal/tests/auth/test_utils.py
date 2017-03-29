import logging
import traceback

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.dispatch import Signal
from django.core.exceptions import PermissionDenied
from django.conf import settings

from tardis.tardis_portal.auth.utils import get_or_create_user
from tardis.tardis_portal.models import UserProfile, UserAuthentication
from tardis.tardis_portal.views.authentication import cas_callback, rcauth

logger = logging.getLogger(__name__)

class GetOrCreateUserTestCase (TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    '''
    Verify that a user is well formed.
    '''
    def _verifyUser(self, auth_method, user_id):

        # verify Users exist
        all_users = User.objects.all()
        no_users = len(all_users)
        print 'len(all_users) = ', len(all_users)
        print 'no of users = ', no_users
        self.assertIsNotNone(all_users, 'There are no users!')
        self.assertGreater(no_users,0)
        print 'all_users[0].username = ', all_users[0].username

        # verify User
        users = User.objects.filter(username=user_id)
        self.assertIsNotNone(users, 'users list is None!')
        self.assertTrue( (len(users) > 0) , 'users list is empty!')

        auth_method_found = False
        for userX in users:
            self.assertIsNotNone(userX.username, 'user.username is None!')
            self.assertEquals(userX.username, user_id, 'username[%s] not expected[%s]!' % (
                         userX.username, user_id))
            logger.debug("User object is valid!")

            # verify UserProfile
            profile = UserProfile.objects.get(user=userX)
            self.assertIsNotNone(profile, 'UserProfile is None!')
            self.assertIsNotNone(profile.isDjangoAccount, 'isDjangoAccount is None!')
            if auth_method == 'localdb':
                self.assertTrue(profile.isDjangoAccount,
		    'isDjangoAccount is False, but auth_method is %s' % auth_method)
            if auth_method == 'aaf' or auth_method == 'aafe':
                self.assertIsNotNone(profile.rapidConnectEduPersonTargetedID,
                    'targetedID is None, but auth_method is %s' % auth_method)
                self.assertTrue(profile.rapidConnectEduPersonTargetedID,
                    'targetedID is empty, buth auth_method is %s' % auth_method)
            logger.debug("UserProfile object is valid!")

            # verify UserAuthentication
            auth = UserAuthentication.objects.get(userProfile=profile)
            self.assertIsNotNone(auth, 'UserAuthentication is None!')
            logger.debug("auth(%s,%s,%s)" % (auth.username,
                                  auth.authenticationMethod,
                                  auth.getAuthMethodDescription))
            self.assertIsNotNone(auth.username, 'UserAuthentication username is None!')
            self.assertEquals(auth.username, user_id, 'username[%s] not expected[%s]!' % (
                         auth.username, user_id))
            self.assertIsNotNone(auth.authenticationMethod, 'auth.auth_method is None!')
            if auth.authenticationMethod == auth_method:
                auth_method_found = True
                logger.debug("UserAuthentication object is valid!")

        logger.debug('auth_method_found = %s' % auth_method_found)
        self.assertTrue(auth_method_found,
            'UserAuthentication not found for username[%s] and auth_method[%s]!' % (
                auth.username, auth_method))

        return True


    '''
    Test creation of local user
    '''
    def testLocalUser(self):
        method = "localdb"
        user_id = "adminX1"
        email = "admin_x@dummy.edu.au"

        # create user
        (result, created) = get_or_create_user(method, user_id, email)
        self.assertIsNotNone(result, 'returned localdb user is None!')
        self.assertTrue(created, 'returned created flag is False')
        self.assertTrue(self._verifyUser(method,user_id), 'localdb user not verified!')

        return


    '''
    Test creation of CAS user
    '''
    def testCASUser(self):
        method = 'cas'
        user_id = 'casUser1'

        # create user
        try:
            pass
            #cas_callback(self.__class__, user=user_id)
        except Exception as ex:
            traceback.print_exc()
            self.fail('cas_callback() raised exception: %s[%s]' % (type(ex).__name__, ex.args[0]))
        
        #self.assertTrue(self._verifyUser(method, user_id), 'cas user not verified!')
        return


    '''
    Test creation of AAF user
    '''
    def testAAFUser(self):
        method = 'aaf'
        user_id = 'aafUser1'
        targetedID = 'ALK/^9)6,123L;K98QWERKJL'
        request = RequestFactory().get('/auth/jwt/rc')
        try:
            rcauth(request)
            self.fail('rcauth() did not raise PermissionDenied')
        except PermissionDenied:
            pass
        except Exception, e:
            self.fail('Invalid exception raised[%s] not[PermissionDenied]' % e)

        # format valid request
        request.method = "POST"
        attributes = {}
        attributes['id'] = user_id
        attributes['email'] = '%s@%s' % (user_id, settings.LOGIN_HOME_ORGANIZATION)
        attributes['edupersionscopedaffiliation'] = '%s@%s' % ('staff', settings.LOGIN_HOME_ORGANIZATION)
        attributes['edupersontargetedid'] = targetedID
        session = self.client.session
        session['attributes'] = attributes
        request.session = session

        try:
            pass
            # rcauth(request)
        except Exception as ex:
            traceback.print_exc()
            self.fail('rcauth() raised exception: %s[%s]' % (type(ex).__name__, ex.args[0]))

        #self.assertTrue(self._verifyUser(method, user_id), 'aaf user not verified!')
        return


    '''
    Test creation of AAFE user
    '''
    def testAAFEUser(self):
        
        return
