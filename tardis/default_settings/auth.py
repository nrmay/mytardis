USER_PROVIDERS = (
    'tardis.tardis_portal.auth.localdb_auth.DjangoUserProvider',
)

GROUP_PROVIDERS = (
    'tardis.tardis_portal.auth.localdb_auth.DjangoGroupProvider',
    'tardis.tardis_portal.auth.token_auth.TokenGroupProvider',
)

# AUTH_PROVIDERS entry format:
# ('name', 'display name', 'backend implementation')
#   name - used as the key for the entry
#   display name - used as the displayed value in the login form
#   backend implementation points to the actual backend implementation
#
#   In most cases, the backend implementation should be a fully
#   qualified class name string, whose class can be instantiated without
#   any arguments.  For LDAP authentication, the
#       'tardis.tardis_portal.auth.ldap_auth.LDAPBackend'
#   class can't be instantiated without any arguments, so the
#       'tardis.tardis_portal.auth.ldap_auth.ldap_auth'
#   wrapper function should be used instead.
#
# We will assume that localdb will always be a default AUTH_PROVIDERS entry

AUTH_PROVIDERS = (
    ('localdb', 'Local DB',
     'tardis.tardis_portal.auth.localdb_auth.DjangoAuthBackend'),
)


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'tardis.tardis_portal.auth.authorisation.ACLAwareBackend',
)

MANAGE_ACCOUNT_ENABLED = True

AUTOGENERATE_API_KEY = False
'''
Generate a tastypie API key with user post_save
(tardis/tardis_portal/models/hooks.py)
'''

# default authentication module for experiment ownership user during
# ingestion? Must be one of the above authentication provider names
DEFAULT_AUTH = 'localdb'

AUTH_PROFILE_MODULE = 'tardis_portal.UserProfile'

# New users are added to these groups by default.
NEW_USER_INITIAL_GROUPS = []

# Turn on/off the self-registration link and form
REGISTRATION_OPEN = True
# or disable registration app (copy to your settings.py first!)
# INSTALLED_APPS = filter(lambda x: x != 'registration', INSTALLED_APPS)
ACCOUNT_ACTIVATION_DAYS = 3

# ---------------------------------
# Log In Method settings
# ---------------------------------
''' Sets the front-end used by the default login button on the portal_template.
'''
LOGIN_FRONTEND_DEFAULT = "local"

''' LOGIN_FRONTENDS defines the different methods that are supported by the
mutli-modal login interface. By default only the 'mytardis' login is enabled.
Fields include: id, display label, enabled flag, and .
'''
LOGIN_FRONTENDS = {
    'local':   {'label':'Local', 'enabled':True,  'groups': set()},
    'aaf':     {'label':'AAF',   'enabled':False, 'groups': set()},
    'aafe':    {'label':'Home',  'enabled':False, 'groups': set()},
    'saml2':   {'label':'SAML2', 'enabled':False, 'groups': set()},
}

''' The home organization is used to strip the domain from email addresses to
identify the organizational user id.
'''
LOGIN_HOME_ORGANIZATION = ''

# SAML2 Server default settings
SAML2_AUTH = {
    # Metadata is required, choose either remote url or local file path
    'METADATA_AUTO_CONF_URL': '[The auto(dynamic) metadata configuration URL of SAML2]',
    'METADATA_LOCAL_FILE_PATH': '[The metadata configuration file path]',

    # Optional settings below
    'DEFAULT_NEXT_URL': '/admin',  # Custom target redirect URL after the user get logged in. Default to /admin if not set. This setting will be overwritten if you have parameter ?next= specificed in the login URL.
    'CREATE_USER': 'TRUE', # Create a new Django user when a new user logs in. Defaults to True.
    'NEW_USER_PROFILE': {
        'USER_GROUPS': [],  # The default group name when a new user logs in
        'ACTIVE_STATUS': True,  # The default active status for new users
        'STAFF_STATUS': True,  # The staff status for new users
        'SUPERUSER_STATUS': False,  # The superuser status for new users
    },
    'ATTRIBUTES_MAP': {  # Change Email/UserName/FirstName/LastName to corresponding SAML2 userprofile attributes.
        'email': 'Email',
        'username': 'UserName',
        'first_name': 'FirstName',
        'last_name': 'LastName',
    },
    'TRIGGER': {
        'CREATE_USER': 'path.to.your.new.user.hook.method',
        'BEFORE_LOGIN': 'path.to.your.login.hook.method',
    },
    'ASSERTION_URL': 'https://mysite.com', # Custom URL to validate incoming SAML requests against
    'ENTITY_ID': 'https://mysite.com/saml2_auth/acs/', # Populates the Issuer element in authn request
    'NAME_ID_FORMAT': '', # FormatString, # Sets the Format property of authn NameIDPolicy element
    'USE_JWT': False, # Set this to True if you are running a Single Page Application (SPA) with Django Rest Framework (DRF), and are using JWT authentication to authorize client users
    'FRONTEND_URL': 'https://myfrontendclient.com', # Redirect URL for the client if you are using JWT auth with DRF. See explanation below
}


# Show the Rapid Connect login button.
''' AAF RAPID CONNECT configuration parameters...
iss: 'https://rapid.test.aaf.edu.au' or 'https://rapid.aaf.edu.au'
aud: the service URL entered as part of the AAF registation process.
secret: key entered as part of the AAF registration process.
authnrequesst_url: the url generated by AAF as confirmation of successful
service registration,
e.g. 'https://rapid.test.aaf.edu.au/jwt/authnrequest/research/XXXXXXXXXXXXXXXX'

NOTE: when registering the service use the following callback url:
     'https://<url of the mytardis instance>/rc/auth/jwt/'

NOTE: if set, the LOGIN_HOME_ORGANIZATION will be strip from the
      edupersonprincipalname to extract the user id within the domain.
      eg. set the domain to 'example.com' to convert 'u99999@example.com'
      into a user id of 'u99999'.

NOTE: the optional 'entityID' must be set if the 'aafe' login frontend is
      enabled. This parameter will be appended to the AAF login request
      to automatically redirect to the selected identity provider.
      Refer to the following url for your organizations end-point:
      https://manager.test.aaf.edu.au/federationregistry/membership/identityprovider/list
'''
RAPID_CONNECT_CONFIG = {}
RAPID_CONNECT_CONFIG['iss'] = 'https://rapid.test.aaf.edu.au'
RAPID_CONNECT_CONFIG['aud'] = 'https://<url of the tardis instance>/'
RAPID_CONNECT_CONFIG['secret'] = 'CHANGE_ME'
RAPID_CONNECT_CONFIG['authnrequest_url'] = ''
RAPID_CONNECT_CONFIG['entityID'] = ''

# ---------------------------------
