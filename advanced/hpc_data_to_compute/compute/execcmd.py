import os
from subprocess import PIPE, Popen
#import irods_types
from os.path import (expanduser, 
                     sep as SEP, pardir as PARENT_DIR, curdir as CURRENT_DIR,
                     split as path_split, join as path_join)

__all__ = [ "run_execCmd" ]

ALLOWABLE_PATH_TO_EXECUTABLES = os.path.expanduser ("~irods/msiExecCmd_bin")
assert os.path.isdir (ALLOWABLE_PATH_TO_EXECUTABLES)

# Constraints:
# 1 arg0 and argList are strings
# 2 arg0 may not contain spaces
# 3 arguments within argList that contain spaces should be quoted

def run_execCmd_using_iRODS( arg0, argList, callback):

  if True: 
    raise NotImplementedError(
      "PREP issue 11 - msiExecCmd not usable from Python Rules" 
    )
  else:
    ret_val = callback.msiExecCmd ( arg0 , argList , "null", "null", "null", irods_types.ExecCmdOut() ) 
    return ret_val['status'] == True

def run_execCmd_using_unix( arg0, argList, collect_output,
                            callback = None):

  if SEP not in arg0:
    arg0 =  path_join(ALLOWABLE_PATH_TO_EXECUTABLES, arg0)
  else:
    return False

  if collect_output is not None:
    assert type(collect_output) is list, 'list obj needed to collect output'
  else:
    collect_output = []

  p = Popen( arg0 + " " + argList.strip() , shell = True, 
        stdout = PIPE, stderr = PIPE)

  collect_output[:] = p.communicate() 
  return (p.returncode == 0)

def run_execCmd ( arg0, argList, collect_output = None, callback = None ):

  return run_execCmd_using_unix( arg0, argList, collect_output, callback )

#-----------------------------------------------

if __name__ == '__main__':

  # test :

  out_err = []
  args = "one 'two_a  Two_b' 'three'"
  run_execCmd( "hello", args, out_err )

  print ("Output of hello with args={0!r} is : {1!r}".format(
     args,
     { 'stdout' : out_err[0] ,  'stderr' : out_err[1] }
  ))
