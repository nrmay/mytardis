Filter for SAM/BAM Format
=========================

This filter extracts meta-data from files saved in the SAM/BAM format as described in the following document:

	Title: 		"Sequence Alignment/Map Format Specification" 
   	Date:  		18 October 2013
   	Version: 	6f8dfe4
   	URL:   		http://github.com/samtools/hts-specs

The filter requires the python library: pysam
	
	Version: 	0.7.6
	URL:		http://code.google.com/p/pysam/
	
Configuration
-------------

Add the following lines to the file: settings.py

#Post Save Filters
POST_SAVE_FILTERS += [
   ("tardis.tardis_portal.filters.samformat.samfiles.make_filter",
    ["SAMFORMAT", "http://mytardis.org/samformat/"]),  
]

Testing
-------

Run the following command in the mytardis/current directory:

./bin/django test --settings=tardis.test_settings tardis.tardis_portal.tests.filters.test_samfile

All test should pass.

Schemas
-------

Parameter sets will be extracted from the file header information using the following schemas: 

	Header Line:					http://mytardis.org/samformat/6f8dfe4/header
	Reference Sequence Dictionary*:	http://mytardis.org/samformat/6f8dfe4/sequence
	Read Group*:					http://mytardis.org/samformat/6f8dfe4/group
	Program*:						http://mytardis.org/samformat/6f8dfe4/program
	Comments:						http://mytardis.org/samformat/6f8dfe4/comment

Notes:
	All lines are optional---sam/bam files can be created with no header information.	
	Schemas will be created---when required---from data encoded in the filter __init__ method. 
	*: one parameter set will be created for each instance of these lines.
