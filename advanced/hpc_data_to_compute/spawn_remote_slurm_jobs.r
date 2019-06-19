run_tasks
{
    get_host_and_resource_name_by_role(*host, *resc_name, *role_key, *role_val) 
    writeLine ("stdout", "host=[*host] resc=[*resc_name]")
    if ("*host" == "" ) {
        writeLine ("stdout", "Host for job launch was not found.")
    } else {
        writeLine("stdout","host = *host")
    

    remote(*host, "") {
      *input_file_path = "";get_job_param_as_string("input_path",*input_file_path)
      writeLine("stdout", "hello input ---> *input_file_path")
      foreach (*x in select DATA_PATH,DATA_NAME where 
	  COLL_NAME = '*input_file_path' and
	  RESC_NAME = '*resc_name' and
	  DATA_NAME like '%.jpg' || like '%.gif' || like '%.tif')
      {
	  *input_file_name = *x.DATA_NAME
	  *src_phy_path = *x.DATA_PATH
      }
      writeLine("stdout", "image phy path => *src_phy_path")
      writeLine("stdout", "image data name => *input_file_name")
      *el=split(*input_file_name,".")
      *input_file_stub_name = elem(*el,0)
      *input_file_ext = elem(*el,1)

      *thumbnail_sizes = ""
      get_job_param_as_string("thumbnail_sizes",*thumbnail_sizes)
  #     *dst_dir = ""; get_job_param_as_string( "phys_dir_for_output", *dst_dir)
  ####  foreach (*size in split (*thumbnail_sizes, ",")) {
  ##      writeLine ("serverLog", "job for thumbnail size : [*size] - running on host [ *host ]")
  ##      *dst_phy_path = *dst_dir" ++ "*input_file_stub_name" ++ "_thumbnail_" ++ "*size" ++ "*input_file_ext"
  ##      writeLine ("serverLog", " dst_phy_path --> [*dst_phy_path]")
  #       writeLine("serverLog"," - thumbsize [ *size ]; convert ( *src_phy_path , *dst_phy_path )")
  #       *cmd_opts="/var/lib/irods/msiExecCmd_bin/convert.SLURM -thumbnail *size *src_phy_path *dst_phy_path"
  #       msiExecCmd("submit_thumbnail_job.sh","*cmd_opts","null","null","null",*OUT)
  ####  } #foreach
    } #remote
    } #if-else
} # end rule

get_host_and_resource_name_by_role (*host, *resc_name, *attr, *value) 
{
    *host = ""
    *resc_name = ""
    *out1=*attr
    *out2=*value
    if (*value == "") { # assume *attr is of form "KEY=VALUE"
      *in = *attr
      parse_role_spec (*in, *attr, *value)
    }

    foreach(*row in SELECT DATA_RESC_NAME WHERE META_RESC_ATTR_NAME = '*out1' AND 
                    META_RESC_ATTR_VALUE = '*out2') {
        *resc_name = *row.DATA_RESC_NAME
    }

    foreach (*h in SELECT RESC_LOC WHERE DATA_RESC_NAME = '*resc_name' )
    {
      *host = *h.RESC_LOC;
    }
}

parse_role_spec (*in, *atr, *value)
{
  *el = split(*in,"=")
  if (size(*el) == 2 && *value == "") { *atr=elem(*el,0); *value = elem(*el,1) }
}

INPUT *role_key="COMPUTE_RESOURCE_ROLE",*role_val="IMAGE_PROCESSING"
OUTPUT ruleExecOut
