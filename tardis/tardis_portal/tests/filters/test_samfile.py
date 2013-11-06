"""
Created on Oct 30, 2013

.. moduleauthor:: Nick May <nicholasmay2@gmail.com>

"""
import unittest
from os import path
from compare import expect

from django.test import TestCase

from tardis.tardis_portal.filters.samfiles import Samfilter 

from tardis.tardis_portal.models import User, UserProfile, Location, Experiment, Dataset, \
    ObjectACL, Dataset_File, Replica
from tardis.tardis_portal.models import Schema, DatafileParameterSet
from tardis.tardis_portal.models import ParameterName, DatafileParameter
from tardis.tardis_portal.tests.test_download import get_size_and_sha512sum 


class SAMFormatTestCase(TestCase):


    def setUp(self):
        # Create test owner without enough details
        username, email, password = ('testuser',
                                     'testuser@example.test',
                                     'password')
        user = User.objects.create_user(username, email, password)
        profile = UserProfile(user=user, isDjangoAccount=True)
        profile.save()

        Location.force_initialize()

        # Create test experiment and make user the owner of it
        experiment = Experiment(title='Text Experiment',
                                institution_name='Test Uni',
                                created_by=user)
        experiment.save()
        acl = ObjectACL(
            pluginId='django_user',
            entityId=str(user.id),
            content_object=experiment,
            canRead=True,
            isOwner=True,
            aclOwnershipType=ObjectACL.OWNER_OWNED,
        )
        acl.save()

        dataset = Dataset(description='dataset description...')
        dataset.save()
        dataset.experiments.add(experiment)
        dataset.save()
        
        def create_datafile(index):
            testfile = path.join(path.dirname(__file__), 'fixtures',
                                 'samfile_test%d.sam' % index)

            size, sha512sum = get_size_and_sha512sum(testfile)

            datafile = Dataset_File(dataset=dataset,
                                    filename=path.basename(testfile),
                                    size=size,
                                    sha512sum=sha512sum)
            datafile.save()
            base_url = 'file://' + path.abspath(path.dirname(testfile))
            location = Location.load_location({
                'name': 'test-sam', 'url': base_url, 'type': 'external',
                'priority': 10, 'transfer_provider': 'local'})
            replica = Replica(datafile=datafile,
                              url='file://'+path.abspath(testfile),
                              protocol='file',
                              location=location)
            replica.verify()
            replica.save()
            return Dataset_File.objects.get(pk=datafile.pk)

        self.dataset = dataset
        self.datafiles = [create_datafile(i) for i in (1,2)]
        
    def tearDown(self):
        # DatafileParameterSet, Parameters
#         params = DatafileParameter.objects.all()
#         for param in params:
#             param.delete()
#         dfpsets = DatafileParameterSet.objects.all()
#         for pset in dfpsets:
#             pset.delete()
#          
#         # delete all Schemas, ParameterNames
#         schemas = Schema.objects.all()
#         for schema in schemas:
#             pnames = ParameterName.objects.filter(schema=schema)
#             for pname in pnames:
#                 pname.delete()                                       
#             schema.delete()
#             
#         # delete all Dataset_Files
#         files = Dataset_File.objects.all()
#         for f in files:
#             sets = f.getParameterSets()
#             for s in sets:
#                 s.delete()
#             f.delete()
 
        # finished
        return

    # ------------------------------------
    # verify the schema namespace
    # ------------------------------------
    def testSchemaNamespace(self):
        # test small sam file: with one HD and SQ lines
        samformat = 'SAMFORMAT'
        version="6f8dfe4"
        schema = 'http://mytardis.org/samformat/noend'
        fullname = schema + "/" + version + "/"
         
        # run filter
        Samfilter(samformat,schema)(None, instance=self.datafiles[0])
         
        # get datafile
        datafile = Dataset_File.objects.get(id=self.datafiles[0].id)
        self.assertEqual(datafile.id,self.datafiles[0].id,"datafile id not matched!")
                 
        # Check that two schemas were created
        print "schema count = %d " % Schema.objects.all().count()
         
        # check schemas
        schemas = Schema.objects.filter(namespace__startswith=fullname)
        self.assertEqual(schemas.count(),2,"schema count not matched!")
        schemas = Schema.objects.filter(namespace__exact=fullname + 'header')
        self.assertEqual(schemas.count(),1,"schema for header count not matched!")
        schemas = Schema.objects.filter(namespace__exact=fullname + 'sequence')
        self.assertEqual(schemas.count(),1,"schema for sequence count not matched!")   
        schemas = Schema.objects.filter(namespace__exact=fullname + 'group')
        self.assertEqual(schemas.count(),0,"schema for group count not matched!")
    
        # finished
        return     

    # ------------------------------------
    # verify a small header 
    # ------------------------------------
    def testSmallHeader(self):
        # test small sam file: with one HD and SQ lines
        samformat = 'SAMFORMAT'
        version="6f8dfe4"
        schema = 'http://mytardis.org/samformat/small/'
        fullname = schema + version + "/"
         
        # run filter
        Samfilter(samformat,schema)(None, instance=self.datafiles[0])
         
        # get datafile
        datafile = Dataset_File.objects.get(id=self.datafiles[0].id)
        self.assertEqual(datafile.id,self.datafiles[0].id,"datafile id not matched!")
         
        # Check that two schemas were created
        print "schema count = %d " % Schema.objects.all().count()
         
        # check schemas
        schemas = Schema.objects.filter(namespace__startswith=fullname)
        self.assertEqual(schemas.count(),2,"schema count not matched!")
         
        # check header line
        try:
            # check schema
            schemaname = fullname + 'header'
            schema = Schema.objects.get(namespace__exact=schemaname)
            print 'schema[' + schemaname + '] exists'
             
            # check header parameter names
            param_names = ParameterName.objects.filter(schema=schema)
            self.assertEqual(param_names.count(),2,"parameter names not matched for " + schemaname)
            param = param_names.get(name__exact='format')
            expect(param.full_name).to_equal('Format Version')
            expect(param.data_type).to_equal(ParameterName.STRING)
            param = param_names.get(name__exact='sorting')
            expect(param.full_name).to_equal('Sorting Order')
            expect(param.data_type).to_equal(ParameterName.STRING)
            print 'schema[' + schemaname + '] parameter names matched'
             
            # check parameter sets
            pset = datafile.getParameterSets().filter(schema__exact=schema)
            self.assertEqual(pset.count(),1,"count of header parametersets not matched!")
             
            # Check all the expected parameters are there
            psm = pset[0]
            pname = 'format'
            expect(psm.get_param(pname).string_value).to_equal('1.0')
         
                        
        except DatafileParameter.DoesNotExist:
            self.fail('DatafileParameter[name=\'' + pname + '\'] not found')    
     
        except Schema.DoesNotExist:
            self.fail('Schema[\'' + schemaname + '\'] not found')    
             
        # check sequence line
        try:
            # check schema 
            schemaname = fullname + 'sequence'
            schema = Schema.objects.get(namespace__exact=schemaname)
            print 'schema[' + schemaname + '] exists'
 
            # check sequence parameter names
            param_names = ParameterName.objects.filter(schema=schema)
            self.assertEqual(param_names.count(),6,"parameter names not matched for " + schemaname)
            param = param_names.get(name__exact='name')
            expect(param.full_name).to_equal('Reference Sequence Name')
            expect(param.data_type).to_equal(ParameterName.STRING)
            param = param_names.get(name__exact='length')
            expect(param.full_name).to_equal('Sequence Length')
            expect(param.data_type).to_equal(ParameterName.NUMERIC)
            param = param_names.get(name__exact='genome')
            param = param_names.get(name__exact='md5')
            param = param_names.get(name__exact='species')
            param = param_names.get(name__exact='uri')
            print 'schema[' + schemaname + '] parameter names matched'
             
            # check parameter sets
            pset = datafile.getParameterSets().filter(schema__exact=schema)
            self.assertEqual(pset.count(),1,"count of sequence parametersets not matched!")
             
            # Check all the expected parameters are there
            psm = pset[0]
            pname = 'length'
            expect(psm.get_param(pname).numerical_value).to_equal(48297693)
            pname = 'name'
            expect(psm.get_param(pname).string_value).to_equal('2')
                  
        except DatafileParameter.DoesNotExist:
            self.fail('DatafileParameter[name=\'' + pname + '\'] not found')    
     
        except Schema.DoesNotExist:
            self.fail('check schema[' + schemaname + '] failed')
 
 
        # check parameter sets
        paramsets = datafile.getParameterSets()
        self.assertEqual(paramsets.count(),2,"datafile parameterset count not matched!")      
   
        # Check we won't create a duplicate dataset
        Samfilter(samformat,schema)(None, instance=self.datafiles[0])
        dataset = Dataset.objects.get(id=self.dataset.id)
        expect(dataset.getParameterSets().count()).to_equal(0)
         
 
        # finished testSmallHeader
        return
 
    # ------------------------------------
    # verify a large header with all lines
    # ------------------------------------
    def testLargeHeader(self):
        # test small sam file: with one HD and SQ lines
        samformat = 'SAMFORMAT'
        version="6f8dfe4"
        schema = 'http://mytardis.org/samformat/large/'
        fullname = schema + version + "/"
          
        # run filter
        Samfilter(samformat,schema)(None, instance=self.datafiles[1])
          
                # get datafile
        datafile = Dataset_File.objects.get(id=self.datafiles[1].id)
        self.assertEqual(datafile.id,self.datafiles[1].id,"datafile id not matched!") 
          
        # Check that schemas were created
        print "schema count = %d " % Schema.objects.all().count()
        for item in Schema.objects.all():
            print 'Found Schema = ' + str(item)
            for name in ParameterName.objects.filter(schema=item):
                print'   Found ParameterName = ' + str(name)
          
        # check schemas
        schemas = Schema.objects.filter(namespace__startswith=fullname)
        self.assertEqual(schemas.count(),5,"schema count not matched!")
                  
        # check header line
        try:
            # check schema
            schemaname = fullname + 'header'
            schema = Schema.objects.get(namespace__exact=schemaname)
            print 'schema[' + schemaname + '] exists'
            
            # check parameter sets
            pset = datafile.getParameterSets().filter(schema__exact=schema)
            self.assertEqual(pset.count(),1,"count of sequence parametersets not matched!")
             
            # Check all the expected parameters are there
            psm = pset[0]
            pname = 'format'
            expect(psm.get_param(pname).string_value).to_equal('1.0')
            pname = 'sorting'
            try:
                psm.get_param(pname)
                self.fail('DatafileParameter[name=\'' + pname + '\'] found in error.')
            except DatafileParameter.DoesNotExist:
                print 'ok! missing DatafileParameter[name=\'' + pname + '\']  expected.'
               
        except DatafileParameter.DoesNotExist:
            self.fail('DatafileParameter[name=\'' + pname + '\'] not found')    
     
        except Schema.DoesNotExist:
            self.fail('schema[' + schemaname + '] failed')    
              
        # check sequence line
        try:
            # check schema 
            schemaname = fullname + 'sequence'
            schema = Schema.objects.get(namespace__exact=schemaname)
            print 'schema[' + schemaname + '] exists'
              
            # check parameter sets
            pset = datafile.getParameterSets().filter(schema__exact=schema)
            self.assertEqual(pset.count(),2,"count of sequence parametersets not matched!")
             
            # Check all the expected parameters are there
            psm = pset[0]
            pname = 'name'
            pvalue = psm.get_param(pname).string_value
            pname = 'length'
            if pvalue == 'chr1':
                expect(psm.get_param(pname).numerical_value).to_equal(1575)
            elif pvalue == 'chr2':
                expect(psm.get_param(pname).numerical_value).to_equal(1584)
            else:
                self.fail('unknown sequence name[' + pvalue + '] found!')
                   
        except DatafileParameter.DoesNotExist:
            self.fail('DatafileParameter[name=\'' + pname + '\'] not found')    
            
        except Schema.DoesNotExist:
            self.fail('schema[' + schemaname + '] failed')
  
        # check group line
        try:
            # check schema 
            schemaname = fullname + 'group'
            schema = Schema.objects.get(namespace__exact=schemaname)
            print 'schema[' + schemaname + '] exists'
  
            # check sequence parameter names
            param_names = ParameterName.objects.filter(schema=schema)
            expect(param_names.count()).to_equal(12)
            param = param_names.get(name__exact='date')
            expect(param.full_name).to_equal('Run Date')
            expect(param.data_type).to_equal(ParameterName.DATETIME)
             
            # check DatafileParameterSet
            # TODO: implement
            
        except Schema.DoesNotExist:
            self.fail('schema[' + schemaname + '] failed')
  
        # check program line
        try:
            # check schema 
            schemaname = fullname + 'program'
            schema = Schema.objects.get(namespace__exact=schemaname)
            print 'schema[' + schemaname + '] exists'
  
            # check sequence parameter names
            param_names = ParameterName.objects.filter(schema=schema)
            expect(param_names.count()).to_equal(5)
            
            # check DatafileParameterSet
            # TODO: implement
              
        except Schema.DoesNotExist:
            self.fail('schema[' + schemaname + '] failed')
  
        # check comment line
        try:
            # check schema 
            schemaname = fullname + 'comment'
            schema = Schema.objects.get(namespace__exact=schemaname)
            print 'schema[' + schemaname + '] exists'
  
            # check sequence parameter names
            param_names = ParameterName.objects.filter(schema=schema)
            expect(param_names.count()).to_equal(1)
             
            # check parameter sets
            pset = datafile.getParameterSets().filter(schema__exact=schema)
            self.assertEqual(pset.count(),2,"count of comment parametersets not matched!")
             
            # Check all the expected parameters are there
            pname = 'comment'
            expect(pset[0].get_param(pname).string_value).to_equal('this is a comment')
            expect(pset[1].get_param(pname).string_value).to_equal('this is another comment')
               
        except DatafileParameter.DoesNotExist:
            self.fail('DatafileParameter[name=\'' + pname + '\'] not found')   
              
        except Schema.DoesNotExist:
            self.fail('schema[' + schemaname + '] does not exist')
  
  
  
        # check parameter sets
        dataset = Dataset.objects.get(id=self.dataset.id)
        expect(dataset.getParameterSets().count()).to_equal(0)
  
  
        # Check we won't create a duplicate dataset
        Samfilter(samformat,schema)(None, instance=self.datafiles[1])
        dataset = Dataset.objects.get(id=self.dataset.id)
        expect(dataset.getParameterSets().count()).to_equal(0)
          
  
        # finished testSmallHeader
        return
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()