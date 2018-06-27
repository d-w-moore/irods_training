# --- 
# allow normal rodsuser to register files into iRODS

# -- this rule set should exist HPC server side only!

acSetChkFilePathPerm { msiSetChkFilePathPerm("noChkPathPerm"); }

rmtExec_singularity2 ( *compute_container_args, *intermediate_args, *postproc_container_args )
{
  msiExecCmd("hello2", "*postproc_container_args", "null", "null", "null",  *OUT);
}

rmtExec_singularity( *compute_container_args, *intermediate_args, *postproc_container_args )
{
  *user = ""

  get_irods_username (*user)
  
  if (*user != '') {
    msiExecCmd("submit_contained_job_via_Slurm.sh", "/var/lib/irods/compute/singularity.SLURM " ++
               " -u *user *intermediate_args --postproc '*postproc_container_args' "++
               " *compute_container_args",
               "null","null","null",*OUT)
  }
}



