#!/usr/bin/env python
from __future__ import print_function
from subprocess import Popen,PIPE
from getopt import getopt
from sys import path as python_path, argv, exit, stderr as STDERR
from os.path import join as UNIX_join,dirname
from os import environ
import pprint

python_path.insert(0, UNIX_join(environ['HOME'],'compute'))
import common

null = open('/dev/null','w')
SBATCH_OPTIONS="--export ALL -o /tmp/slurm-%j.out"
SCRIPT=""
VERBOSE=0

opts, args = getopt (argv[1:],'v', [ 'input=', 'script=', 'verbose='])
params = common.jobParams()
SCRIPT = params.get( "thumbnail_convert_script", "")

Input_image_logical_path = ""

for k,v in opts:
    if k == '--input': Input_image_logical_path = v
    elif k == '--script': SCRIPT=v
    elif k == '-v': VERBOSE=1
    elif k == '--verbose': VERBOSE=int('0'+v,10)

if not Input_image_logical_path.startswith ("/"):
    print ( "--input value (logical path) needs absolute path", file=STDERR)
    exit(121)

scratch_resc = common.rescName_from_role_KVP( params["imageCompute_resc"] )

(Path,Basename) = Input_image_logical_path.rsplit("/",1)
(Filename,Extension) = Basename.rsplit(".",1)

relpath_for_output = params["relative_path_for_output"]

if not SCRIPT:
    print("Need a script to run",file=STDERR)
    exit(122)
else:
    if VERBOSE:
        print('SCRIPT is {!r}'.format(SCRIPT),file=STDERR)

env_constants = { 'COMPUTE_JOB_TYPE':'generate_thumbnails',
                  #--------------------------------------
                  'PARAM_data_object_logical_path': Input_image_logical_path, # for debug -- DWM
                  'PARAM_input_image_collection':   Path,
                  'PARAM_input_image_name':         Filename,
                  'PARAM_input_image_extension':    Extension,
                  'PARAM_logical_output_path':      Path + '/' + relpath_for_output,
                }

# --- execute one `sbatch` command per job ---

for size_string in params["thumbnail_size_list"]:

    env_vars = dict( environ )
    env_vars.update( env_constants )

    Use_Key = common.add_usage( Input_image_logical_path, scratch_resc )
    common.replicate_to_resource ( Input_image_logical_path, scratch_resc)

    physical_input_objpath = common.get_data_object_physical_path (Path, Basename, scratch_resc)
    physical_input_dirpath = dirname(physical_input_objpath)

    env_vars['PARAM_thumbnail_size']        = size_string
    env_vars['PARAM_scratch_resource_name'] = scratch_resc
    env_vars['PARAM_resource_use_key']      = Use_Key
    env_vars['PARAM_physical_output_path']  = UNIX_join( physical_input_dirpath, relpath_for_output )

    convert_args = [ '-thumbnail', size_string, physical_input_objpath,
      # the convert script will calculate the last argument, phys_output_path
    ]

    if VERBOSE:
        print ('--- dwm ---',file=STDERR)
        print('convert_args =',file=STDERR); pprint.pprint(convert_args, stream=STDERR)
        print('env_vars =',file=STDERR);     pprint.pprint(env_vars, stream=STDERR)

    p = Popen( ['/usr/local/bin/sbatch'] + SBATCH_OPTIONS.split() + [SCRIPT] + convert_args, 
              stdout = PIPE,
              stderr = null, env = env_vars )

    stdout_text = p.stdout.read()
    if VERBOSE:
        print( 'slurm job output -> ',stdout_text, file=STDERR )
        if VERBOSE > 1: break # -- DWM

    if p.wait() != 0:
        print(argv[0] + " : Error submitting slurm batch job(s)", file=STDERR)

