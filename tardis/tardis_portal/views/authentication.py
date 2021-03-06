"""
views that have to do with authentication
"""

from urlparse import urlparse

import logging
import sys
import jwt
import pwgen

from django.conf import settings
from django.contrib import auth as djauth
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver
from django_cas_ng.signals import cas_user_authenticated

from tardis.tardis_portal.auth import auth_service
from tardis.tardis_portal.auth.utils import get_or_create_user
from tardis.tardis_portal.auth.localdb_auth import auth_key as localdb_auth_key
from tardis.tardis_portal.forms import ManageAccountForm, CreateUserPermissionsForm, \
    LoginForm
from tardis.tardis_portal.models import JTI, UserProfile, UserAuthentication
from tardis.tardis_portal.shortcuts import render_response_index
from tardis.tardis_portal.views.utils import _redirect_303
from tardis.tardis_portal.views.pages import get_multimodal_context_data

logger = logging.getLogger(__name__)


@receiver(cas_user_authenticated)
def cas_callback(sender, **kwargs):
    logger.debug('_cas_callback() start!')
    for key,value in kwargs.iteritems():
        logger.debug('kwargs[%s] = %s' % ( str(key), str(value) ))
        if key == 'user':
            try:
                email = '%s@%s' % (value, settings.LOGIN_HOME_ORGANIZATION)
                authMethod = 'cas'
                logger.debug("user[%s] authMethod[%s] email[%s]"% (
			value,authMethod,email))
                user, created = get_or_create_user('cas', value, email)
                if created:
                    logger.debug('user created = %s' % str(user))
                else:
                    logger.debug('user creation failed!')
            except Exception, e:
                logger.error("get_or_create_user['%s'] failed with %s" % (
                             value, e))

    return

@csrf_exempt
def rcauth(request):
    logger.debug('rcauth() start!')
    # Only POST is supported on this URL.
    if request.method != 'POST':
        raise PermissionDenied

    # Rapid Connect authorization is disabled, so don't process anything.
    if ( not settings.LOGIN_FRONTENDS['aaf']['enabled'] and
         not settings.LOGIN_FRONTENDS['aafe']['enabled'] ):
        raise PermissionDenied

    try:
        # Verifies signature and expiry time
        verified_jwt = jwt.decode(
            request.POST['assertion'],
            settings.RAPID_CONNECT_CONFIG['secret'],
            audience=settings.RAPID_CONNECT_CONFIG['aud'])

        # Check for a replay attack using the jti value.
        jti = verified_jwt['jti']
        if JTI.objects.filter(jti=jti).exists():
            logger.debug('Replay attack? ' + str(jti))
            request.session.pop('attributes', None)
            request.session.pop('jwt', None)
            request.session.pop('jws', None)
            django_logout(request)
            return redirect('/')
        else:
            JTI(jti=jti).save()

        if verified_jwt['aud'] == settings.RAPID_CONNECT_CONFIG['aud'] and \
           verified_jwt['iss'] == settings.RAPID_CONNECT_CONFIG['iss']:
            request.session['attributes'] = verified_jwt[
                'https://aaf.edu.au/attributes']
            request.session['jwt'] = verified_jwt
            request.session['jws'] = request.POST['assertion']

            institution_email = request.session['attributes']['mail']
            edupersontargetedid = request.session['attributes'][
                                                'edupersontargetedid']
            principalname = request.session['attributes'][
                                                'edupersonprincipalname']

            logger.debug('Successfully authenticated %s via Rapid Connect.' %
                         institution_email)

            # Create a user account and profile automatically. In future,
            # support blacklists and whitelists.
            first_name = request.session['attributes']['givenname']
            c_name = request.session['attributes'].get('cn', '').split(' ')
            if not first_name and len(c_name) > 1:
                first_name = c_name[0]
            user_args = {
                'id': institution_email.lower(),
                'email': institution_email.lower(),
                'password': pwgen.pwgen(),
                'first_name': first_name,
                'last_name': request.session['attributes']['surname'],
            }

            # if a principal domain is set strip domain from
            # 'edupersonprincipalname' and use remainder as user id.
            try:
                if settings.LOGIN_HOME_ORGANIZATION:
                    domain = "@" + settings.LOGIN_HOME_ORGANIZATION
                    if ';' not in principalname and \
                        principalname.endswith(domain):
                        user_id = principalname.replace(domain,'').lower()
                        user_args['id'] = user_id
            except:
                logger.debug('check principal domain failed with: %s' %
                             sys.exc_info()[0])

            # Check for an email collision.
            for matching_user in UserProfile.objects.filter(
                    user__email__iexact=user_args['email']):
                if (matching_user.rapidConnectEduPersonTargetedID is not None
                    and matching_user.rapidConnectEduPersonTargetedID !=
                        edupersontargetedid):
                    del request.session['attributes']
                    del request.session['jwt']
                    del request.session['jws']
                    django_logout(request)
                    raise PermissionDenied

            user = get_or_create_user(user_args,authMethod='aaf')
            if user is not None:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                djauth.login(request, user)
                return redirect('/')
        else:
            del request.session['attributes']
            del request.session['jwt']
            del request.session['jws']
            django_logout(request)
            raise PermissionDenied  # Error: Not for this audience
    except jwt.ExpiredSignature:
        del request.session['attributes']
        del request.session['jwt']
        del request.session['jws']
        django_logout(request)
        raise PermissionDenied  # Error: Security cookie has expired
    except Exception, e:
        logger.debug('rcauth() failed with: %s' % e)
        raise PermissionDenied


@login_required
def manage_user_account(request):
    user = request.user

    # Process form or prepopulate it
    if request.method == 'POST':
        form = ManageAccountForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            return _redirect_303('index')
    else:
        form = ManageAccountForm(instance=user)

    c = {'form': form}
    return HttpResponse(render_response_index(request,
                        'tardis_portal/manage_user_account.html', c))


def logout(request):
    if 'datafileResults' in request.session:
        del request.session['datafileResults']

    # Remove AAF attributes.
    del request.session['attributes']
    del request.session['jwt']
    del request.session['jws']

    return redirect('index')


@never_cache
def create_user(request):

    if 'user' not in request.POST:
        c = {'createUserPermissionsForm':
             CreateUserPermissionsForm()}

        response = HttpResponse(render_response_index(
            request,
            'tardis_portal/ajax/create_user.html', c))
        return response

    authMethod = localdb_auth_key

    if 'user' in request.POST:
        username = request.POST['user']

    if 'authMethod' in request.POST:
        authMethod = request.POST['authMethod']

    if 'email' in request.POST:
        email = request.POST['email']

    if 'password' in request.POST:
        password = request.POST['password']

    try:
        with transaction.atomic():
            validate_email(email)
            user = User.objects.create_user(username, email, password)

            authentication = UserAuthentication(userProfile=user.userprofile,
                                                username=username,
                                                authenticationMethod=authMethod)
            authentication.save()

    except ValidationError:
        return HttpResponse('Could not create user %s '
                            '(Email address is invalid: %s)' %
                            (username, email), status=403)
    except:  # FIXME
        return HttpResponse(
            'Could not create user %s '
            '(It is likely that this username already exists)' %
            (username), status=403)

    c = {'user_created': username}
    transaction.commit()

    response = HttpResponse(render_response_index(
        request,
        'tardis_portal/ajax/create_user.html', c))
    return response


def login(request):
    '''
    handler for login page
    '''
    logger.debug("start!")

    if request.user.is_authenticated():
        # redirect the user to the home page if he is trying to go to the
        # login page
        return HttpResponseRedirect(request.POST.get('next_page', '/'))

    # TODO: put me in SETTINGS
    if 'username' in request.POST and \
            'password' in request.POST:
        authMethod = request.POST.get('authMethod', None)

        user = auth_service.authenticate(
            authMethod=authMethod, request=request)

        if user:
            next_page = request.POST.get(
                'next_page', request.GET.get('next_page', '/'))
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            djauth.login(request, user)
            return HttpResponseRedirect(next_page)

        c = {'status': "Sorry, username and password don't match.",
             'error': True,
             'loginForm': LoginForm()}

        c = get_multimodal_context_data(c)

        return HttpResponseForbidden(
            render_response_index(request, 'tardis_portal/login.html', c))

    url = request.META.get('HTTP_REFERER', '/')
    u = urlparse(url)
    if u.netloc == request.META.get('HTTP_HOST', ""):
        next_page = u.path
    else:
        next_page = '/'
    c = {'loginForm': LoginForm(),
         'next_page': next_page}

    c = get_multimodal_context_data(c)

    return HttpResponse(render_response_index(request,
                        'tardis_portal/login.html', c))


@permission_required('tardis_portal.change_userauthentication')
@login_required()
def manage_auth_methods(request):
    '''Manage the user's authentication methods using AJAX.'''
    from tardis.tardis_portal.auth.authentication import add_auth_method, \
        merge_auth_method, remove_auth_method, edit_auth_method, \
        list_auth_methods

    if request.method == 'POST':
        operation = request.POST['operation']
        if operation == 'addAuth':
            return add_auth_method(request)
        elif operation == 'mergeAuth':
            return merge_auth_method(request)
        elif operation == 'removeAuth':
            return remove_auth_method(request)
        else:
            return edit_auth_method(request)
    else:
        # if GET, we'll just give the initial list of auth methods for the user
        return list_auth_methods(request)
