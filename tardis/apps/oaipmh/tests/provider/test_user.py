from compare import expect

from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from django.test import TestCase

import oaipmh.error
import oaipmh.interfaces

import pytz

from tardis.tardis_portal.util import get_local_time

from ...provider.user import RifCsUserProvider

def _create_test_data():
    user = User(username='tom',
                first_name='Thomas',
                last_name='Atkins',
                email='tommy@atkins.net')
    user.save()
    return user

class RifCsUserProviderTestCase(TestCase):

    def _getProvider(self):
        class FakeRequest():
            def get_host(self):
                return 'example.test'
        return RifCsUserProvider(RequestSite(FakeRequest()))

    def setUp(self):
        self._user = _create_test_data()

    def testIdentify(self):
        '''
        There can be only one provider that responds. This one does not.
        '''
        expect(lambda: self._getProvider().identify())\
            .to_raise(NotImplementedError)

    def testGetRecordHandlesInvalidIdentifiers(self):
        for id_ in ['user-1', 'User/1']:
            try:
                self._getProvider().getRecord('rif', id_)
                self.fail("Should raise exception.")
            except oaipmh.error.IdDoesNotExistError:
                pass

    def testListIdentifiers(self):
        headers = self._getProvider().listIdentifiers('rif')
        # Iterate through headers
        for header in headers:
            expect(header.identifier()).to_contain(str(self._user.id))
            expect(header.datestamp().replace(tzinfo=pytz.utc))\
                .to_equal(get_local_time(self._user.last_login))
        # There should only have been one
        expect(len(headers)).to_equal(1)

    def testListIdentifiersDoesNotHandleSets(self):
        def call_with_set():
            self._getProvider().listIdentifiers('rif', set='foo')
        expect(call_with_set).to_raise(oaipmh.error.NoSetHierarchyError)

    def testListMetadataFormats(self):
        expect(map(lambda t: t[0], self._getProvider().listMetadataFormats())) \
            .to_equal(['rif'])

    def testListSets(self):
        try:
            self._getProvider().listSets()
            self.fail("Should throw exception.")
        except oaipmh.error.NoSetHierarchyError:
            pass

    def testGetRecord(self):
        header, metadata, about = self._getProvider().getRecord('rif',
                                                                'user/1')
        expect(header.identifier()).to_contain(str(self._user.id))
        expect(header.datestamp().replace(tzinfo=pytz.utc))\
            .to_equal(get_local_time(self._user.last_login))
        expect(metadata.getField('id')).to_equal(self._user.id)
        expect(metadata.getField('email'))\
            .to_equal(str(self._user.email))
        expect(metadata.getField('given_name'))\
            .to_equal(str(self._user.first_name))
        expect(metadata.getField('family_name'))\
            .to_equal(str(self._user.last_name))
        expect(about).to_equal(None)

    def testListRecords(self):
        results = self._getProvider().listRecords('rif')
        # Iterate through headers
        for header, metadata, _ in results:
            expect(header.identifier()).to_contain(str(self._user.id))
            expect(header.datestamp().replace(tzinfo=pytz.utc))\
                .to_equal(get_local_time(self._user.last_login))
            expect(metadata.getField('id')).to_equal(self._user.id)
            expect(metadata.getField('email'))\
                .to_equal(str(self._user.email))
            expect(metadata.getField('given_name'))\
                .to_equal(str(self._user.first_name))
            expect(metadata.getField('family_name'))\
                .to_equal(str(self._user.last_name))
        # There should only have been one
        expect(len(results)).to_equal(1)

    def tearDown(self):
        pass
