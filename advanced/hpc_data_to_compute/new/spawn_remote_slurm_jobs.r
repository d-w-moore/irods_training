run_tasks
{
  *host = ""
  *key = "COMPUTE_RESOURCE_ROLE"; *val="IMAGE_PROCESSING"
  *resc_name = ""
  get_host_and_resource_name_by_role(*host, *resc_name, *key, *val) 
  writeLine ("stdout", "host=[*host] resc=[*resc_name]")
  if ("*host" == "" ) {
    writeLine ("stdout", "Host for job launch was not found.")
  } else {
    *input_file_path = "";get_job_param_as_string("input_path",*input_file_path)
    foreach (*x in select COLL_NAME,DATA_NAME where COLL_NAME = '*input_file_path' and
                   RESC_NAME = '*resc_name' and DATA_NAME like '%.jpg' || like '%.gif' || like '%.tif') 
    {
     *src_phy_path = *x.DATA_PATH
    }
    remote(*host, "") {
      *el=split(*input_file_path,"/");*input_file_name = elem(*el, size(*el)-1 )
      *thumbnail_sizes = ""; get_job_param_as_string("thumbnail_sizes",*thumbnail_sizes)
      *dst_dir = ""; get_job_param_as_string( "phys_dir_for_output", *dst_dir)
####  foreach (*size in split (*thumbnail_sizes, ",")) {
##      writeLine ("serverLog", "job for thumbnail size : [*size] - running on host [ *host ]")
##      *dst_phy_path = *dst_dir" ++ "*input_file_name" ++ "_thumbnail_" ++ "*size" ++ "*input_file_ext"
##      writeLine ("serverLog", " dst_phy_path --> [*dst_phy_path]")
#       writeLine("serverLog"," - thumbsize [ *size ]; convert ( *src_phy_path , *dst_phy_path )")
#       *cmd_opts="/var/lib/irods/msiExecCmd_bin/convert.SLURM -thumbnail *size *src_phy_path *dst_phy_path"
#       msiExecCmd("submit_thumbnail_job.sh","*cmd_opts","null","null","null",*OUT)
####  } #foreach
    } #remote
  } #if-else
} # end rule


INPUT  null
OUTPUT ruleExecOut
