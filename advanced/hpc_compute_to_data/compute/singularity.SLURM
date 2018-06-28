#!/bin/bash

FUNCTIONS=/var/lib/irods/compute/irods_compute_functions
if [ -r $FUNCTIONS ]; then
  . $FUNCTIONS
fi

EXECUTABLE=~irods/compute/wrap_singularity

outputDir=""

#--------------------------

User=""
if [ "$1" == '-u' ]; then
  User=$2
  shift 2
fi

#--------------------------

while [[ $1 = --* ]] ; do

  if [ "$1" = "--postproc" ] && test_irods_slurm_desc ; then

    postproc_opts=$(delete_u_options $'\x20'"$2")

    if [ $? -eq 0 -a -n "$User" ] ;then 
      postproc_opts+=" -u $User" 
    else
      postproc_opts=""
    fi

    if [ -n "$postproc_opts" ] ; then
      set_irods_slurm_var "post_processing" "$postproc_opts"
      #echo postproc_opts "'$postproc_opts'" >>/tmp/contained_apps_log
    fi
  fi

  if [ "$1" = "--outdir" ]; then
    outputDir="$2"
  fi 

  # - dwm
  # if [ "$1" = "--size" ]; then
  #  sizeStr="$2"
  # fi 

  shift 2

done 

if [ -n "$outputDir" -a ! -d "$outputDir" ]; then
  mkdir -p "$outputDir"
#else # - dwm
#  outputDir="/tmp"
fi

# -- dwm -- 
#{ echo EXECUTABLE '+' ARGS:
#  echo "$EXECUTABLE" "$@" 
#  echo "---------------------"
# } >>/tmp/middle

##- dwm
"$EXECUTABLE" "$@" >>/tmp/middle

