#!/usr/bin/env python

# --
# -  Utility module. Common Python routines for iRODS Data-To-Compute
# --

from __future__ import print_function
import sys, os, time, pprint, uuid, atexit
from os.path import ( join, curdir, dirname, normpath, sep as SEP )
import json
import logging, logging.handlers
from irods.exception import DataObjectDoesNotExist, CollectionDoesNotExist
from irods.models import Resource, ResourceMeta
from irods.models import DataObject, DataObjectMeta
from irods.models import Collection
from irods.column import Criterion, Like
from irods.meta import iRODSMeta
from irods.exception import CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME
import irods.keywords as kw

#----------------------------------------------------------------
# Add resource AVUs if present version of PRC doesn't offer them.
#
from irods.resource import iRODSResource
try:
    iRODSResource.metadata
except:
    import irods.meta
    def resource_metadata(self):
        if not self._meta:
            self._meta = irods.meta.iRODSMetaCollection(
                self.manager.sess.metadata, Resource  , self.name)
        return self._meta
    iRODSResource.metadata = property (resource_metadata)

#----------------------------------------------------------------
# Detect stringish types
#
try:
    stringTypes = (str,unicode)
except:
    stringTypes = (str,)

is_string = lambda s : isinstance(s, stringTypes)
#-----------------------------------------------------------

def get_data_object_physical_path( coll_match , data_match, resc_match ):

    session = session_object()
    NotInTrash = Criterion('not like', Collection.name, '%/trash/%')
    q = session.query(DataObject).filter(
         NotInTrash                    ).filter(
         Collection.name == coll_match ).filter(
         DataObject.name == data_match ).filter(
         Resource.name == resc_match)
    return q.one() [ DataObject.path ]


token32 = lambda : '%032x' % uuid.uuid4()
IRODS_RESC_ACQUIRE_KEY = 'irods::d2c::acquire'


def rm_usage_and_count_remaining(dataObjectToken,rescname):
    sess = session_object()
    resc = sess.resources.get(rescname)
    resc.metadata.remove(iRODSMeta(IRODS_RESC_ACQUIRE_KEY, dataObjectToken))

    (dataobj_path, token) = dataObjectToken.rsplit('--',1)
    dataobj_path = dataobj_path.replace ('_', r'\_')
    token = '_' * len(token)

    usage_query = sess.query(ResourceMeta).filter(
     Resource.name == rescname).filter(
     ResourceMeta.name == IRODS_RESC_ACQUIRE_KEY).filter(
     Like(ResourceMeta.value, dataobj_path + '--' + token ))

    return len(usage_query.all())

def add_usage(data_obj_path, rescname):
    sess = session_object()
    dobj = None
    try:
        dobj = sess.data_objects.get(data_obj_path)
    except:
        pass
    if dobj:
        resc = sess.resources.get(rescname)
        datobj_token = dobj.path + '--' + token32()
        resc.metadata.add(iRODSMeta(IRODS_RESC_ACQUIRE_KEY,datobj_token))
    return datobj_token


def rescName_from_role_KVP ( kvp ):
    session = session_object()
    q = session.query( Resource.name , ResourceMeta.name , ResourceMeta.value )
    q.filter (ResourceMeta.name == kvp[0] and \
              ResourceMeta.value == kvp[1] )
    return q.one()[Resource.name]

def iRODS_slurm_mutx_dir():
    from subprocess import PIPE,Popen
    dir=dict(os.environ,DIR="/var/lib/irods/compute")
    SLURM_Coll = os.environ.get("SLURM_COLLECTION","")
    if not SLURM_Coll:
        SLURM_Coll = Popen(
                         ["bash","-c","source $DIR/slurmcoll.bash >/dev/null; slurm_collection"],
                         stdout=PIPE, stderr=PIPE, env=dir
                     ).communicate()[0].rstrip()
        os.environ[ "SLURM_COLLECTION"] = SLURM_Coll
    return SLURM_Coll

def get_iRODS_home():

    session = session_object()
    path_to_home = "/{}/home/{}".format(session.zone, session.username)
    return path_to_home

def set_job_meta(key,val,units=""):
    mdpath = slurm_job_descriptor_path()
    obj = session_object().data_objects.get(mdpath)
    obj.metadata[key] = iRODSMeta(key,val,units)


#-----------------------------------------------------------

def slurm_job_descriptor_path():
    try:
        return iRODS_slurm_mutx_dir()  + "/" + os.environ['SLURM_CLUSTER_NAME'] + '_slurmjob_' + \
                                               os.environ['SLURM_JOB_ID'] + '.txt'
    except:
        return None

#-----------------------------------------------------------

job_params = {}
logger = None


class dummyLogger (object):
    def __init__(self): pass
    def fatal(self,s): pass
    def error(self,s): pass
    def info (self,s): pass
    def debug(self,s): pass
    def warn (self,s): pass

def computeLogger(use_dummy=False):
    global logger
    if not logger:
        try:
            log_filename =  '/tmp/log_irods_compute.txt' ;
            if not use_dummy:
                logger = logging.getLogger('compute_logger')
                logger.setLevel(logging.DEBUG)
                ch = logging.handlers.WatchedFileHandler(filename=log_filename)
                ch.setFormatter(logging. Formatter('%(filename)s:%(process)d '
                  '@ %(asctime)s - %(message)s') )
                logger.addHandler(ch)
        except:
              pass
    if not logger: logger = dummyLogger()
    return logger


class MetadataNotFoundError(RuntimeError): pass

class MetadataDictFormattable( dict ):

    def __init__( self, elem_dictionary ):
        super(MetadataDictFormattable,self).__init__(self)
        self.update (elem_dictionary)

    def __call__( self, templateString, error_output = None ):

        template = templateString if '{' in templateString else \
            getattr(self, templateString, None)
        if template is None: return error_output
        else:
            return template.format(**self)

    def refresh_job_metadata (self, overwrite_keys=True, overwrite_attrs=True ):
        try:
            desc_path = slurm_job_descriptor_path()
            sess = session_object()
            obj = sess.data_objects.get( desc_path )
        except:
            raise MetadataNotFoundError
        for k,v in [(itm.name,itm.value) for itm in obj.metadata.items()]:
            if overwrite_keys or not self.has_key(k): self[k] = v
        for k,v in self.items():
            if k.startswith("."):
                if overwrite_attrs or not hasattr(self,k[1:]): setattr(self,k[1:],v)
        return self

    def __format__( self, key ):
        return self[key]


class MyDictFormattable( MetadataDictFormattable ):

# -- dwm -- template functionality test -- see ~irods/compute/testit.py
# MY_TEST_STRING = 'thing: uuid = {uuid}.'
# AA = "({uuid})"
# @property
# def CC(self): return self.AA + "..." + self.BB

    @property
    def LONG_TERM_STORAGE_RESC (self):
        return rescName_from_role_KVP( self ["longTermStoreCompute_resc"] )

    @property
    def THUMBNAIL_OUTPUT_DATAOBJECT_FULLPATH(self):
        return self.THUMBNAIL_OUTPUT_COLLECTION + "/" + self.THUMBNAIL_OUTPUT_DATAOBJECT

fmt_job_params = None

def jobParamsPlusMetadata( *x,**kw ):
  global fmt_job_params
  defaultdict =   MyDictFormattable # dwm MetadataDictFormattable
  dictClass = kw.pop('dictClass',defaultdict)
  if not issubclass(dictClass, defaultdict):
      raise ('dictClass arg must be subclass of MetadataDictFormattable')
  j = jobParams(*x,**kw)
  if fmt_job_params is None:
      fmt_job_params = dictClass(j).refresh_job_metadata()
  return fmt_job_params

# -------------------------------------------------------

def jobParams( cfgFile = 'job_params.json' , argv0 = '' ):
    global job_params
    if not(job_params):
        if not argv0: argv0 = __file__
        if SEP not in cfgFile:
            cfgFile = join( (dirname(argv0) or curdir) , cfgFile )
        try:
            job_params = json.load( open( cfgFile, 'r') )
        except:
            msg =  "Could not load JSON config file at {}".format (cfgFile)
            computeLogger().error(msg); raise SystemExit(msg)
    return job_params

session = None

def _clear_session( ):
  # global session # -- dwm -- at times complains when quitting pdb
  g = globals()
  session = globals().get('session')
  if session:
    session.cleanup()
    session = None

def session_object(  ):
  global session
  if session is None:
    from irods.session import iRODSSession
    import os
    try:
      env_file = os.environ ['IRODS_ENVIRONMENT_FILE']
    except KeyError:
      env_file = os.path.expanduser('~/.irods/irods_environment.json')
    session = iRODSSession(irods_env_file = env_file )
    atexit.register(_clear_session)

  return session


def trim_replicas_from_resource ( obj,          # can be data_object, or a full logical path to one
                                  rescName ):
    if is_string(obj): obj=session_object().data_objects.get(obj)
    good_replicas = { r.number:r for r in obj.replicas if r.status == '1' }
    good_replicas_off_resc = { n:r for n,r in good_replicas.items() if r.resource_name != rescName }
    trim_eligible_repl_nums = set(good_replicas.keys()) - set(good_replicas_off_resc.keys())
    if len( good_replicas_off_resc ):
        for n in trim_eligible_repl_nums:
            obj.unlink( replNum = n )

# ---

def _object_path_by_resource( datobj, resourceName ):
    if not datobj: return None
    repls_on_resc = [ repl for repl in datobj.replicas
                     if repl.resource_name == resourceName ]
    if repls_on_resc: return repls_on_resc[0].path
    else:             return None

def _exists_on_resource (dObj, resourceName , test_status = True ):
    _filter = lambda x : x
    if test_status:
        _filter = lambda x : x.status == '1'
    lst = [ r for r in dObj.replicas if r.resource_name == resourceName and _filter(r) ]
    return len(lst) > 0

# - register a file as a data object: will create one sub-collection path element by default

def register_on_resource( absolute_file_path, full_object_path , resc_name , verbose_result = False):
    class RegisterFailure (RuntimeError): pass
    retval = 0
    try:
        if absolute_file_path.startswith('/'):
            absolute_file_path = normpath( absolute_file_path )
        else:
            raise RegisterFailure
        sess = session_object()
        path_elements = full_object_path.rsplit('/',1)
        if len(path_elements) < 2 or get_collection( path_elements[0], create = True) is None:
            raise RegisterFailure
        exists = False
        try:
            sess.data_objects.register( absolute_file_path, full_object_path, rescName = resc_name)
            exists = True
        except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            exists = True
        except:
            exists = False
        datobj = sess.data_objects.get(full_object_path) if exists else None
        retval = -1 if exists and _object_path_by_resource( datobj, resc_name ) != absolute_file_path \
                    else (1 if _exists_on_resource( datobj, resc_name) else 0)
    except RegisterFailure:
        pass
    if verbose_result: print(retval)
    return retval

def replicate_to_resource ( obj, resourceName, **options ):
    sess = session_object()
    datobj = None
    try:
        if is_string(obj):
            datobj = sess.data_objects.get(obj)
        else:
            datobj = obj
        datobj.replicate( resourceName , **options)
        datobj = sess.data_objects.get( datobj.path )
    except:
        datobj = None
    return (datobj is not None) and \
           _exists_on_resource( datobj, resourceName )

def get_collection (collection_name, create = False):
    c = None
    sess = session_object()
    if  not collection_name.startswith('/'): return None
    try:
        c = sess.collections.get( collection_name )
    except CollectionDoesNotExist as e:
        if create: c = sess.collections.create( collection_name )
    return c

#if __name__ == '__main__':
#    add_usage( '/tempZone/home/rods/a.dat', 'demoResc')
#    sys.exit(0)
