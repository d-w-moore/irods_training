#!/usr/bin/env python

from __future__ import print_function
import os, sys
from os.path import sep as SEPARATOR , join, dirname
import json
import pprint

def _str_if_unicode (data, uni_encoding = 'utf8' ):

  if isinstance(data, dict) :
    return { _str_if_unicode(k):_str_if_unicode(v) for k,v in data.items() }
  elif isinstance(data, (list,tuple)) :
    return [ _str_if_unicode(k) for k in data ]
  elif isinstance(data,unicode):
    return data.encode( uni_encoding )
  return data

def str_if_unicode(obj):
  return _str_if_unicode(obj) if sys.version_info < (3,) else obj

class JSON_Config (object):

  def keys(self) : return map(str, self.__lookup.keys())

  def __setitem__( self, k, v ):
    self.__lookup [k] = v

  def __getitem__( self, k ):
    value = self.__lookup.get(k) 
    if type(value) is str and '%(' in value:
      try:
        value %= self.__dict__
      except KeyError as ke:
        pass
    return value

  def __init__(self, file_name):
    if not file_name.lower().endswith(".json"):
      file_name += ".json"
    if SEPARATOR not in file_name :  
      file_name = join(dirname(__file__), file_name)
    self.file_source = file_name
    self.__lookup = {}
    with open(self.file_source, "r") as f:
      kv_pairs_dict = json.load(f, object_hook = str_if_unicode)
      if sys.version_info < (3,):
        self.__lookup = { str(k):v for k,v in kv_pairs_dict.items() }
      else:
        self.__lookup = kv_pairs_dict

if __name__ == '__main__':
  
  thumb = JSON_Config ( "thumbnail_job_parameters" )
  k = thumb.keys()
  for i in k: print ( "{}\t{!r}".format(i,thumb[i]) )

