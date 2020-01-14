main 
{
    *host =  ""
    *context = ""
    application_context_from_input(*host,*context,"*incoll","*data")
    if (*host != "") 
    {
        irods_policy_list_applications (*host, *context , *l) 
        writeLine("stdout",*l)
        *id = '' 
        *err = '' 
        *app_name = full_application_name_from_glob (*app, *l)
        writeLine("stdout","\n===> running container from config: '*app' -> '*app_name' <===\n")
        irods_policy_run_application (*host, *context , '', '*outcoll', '{"DEGREES_ROTATION":"10"}',
                                     '*app_name' ,*id,*err) 
        writeLine("stdout",'id=[*id]')                             
        if (*err != '') { writeLine("stdout",'Application warning/error: [*err]') }
        writeLine("stdout",'ctx=[*context]')
        if (*wait_secs > 0) { msiSleep("*wait_secs","0") }         # to ensure notebook server is up before getting URL
        *exitcode = ""
        *cmd_stdout = "" 
        if (*id != "") {
            irods_policy_exec_command_in_application (*host, *context ,*id, "jupyter notebook list", *exitcode, *cmd_stdout)
            if (*exitcode != "") { 
                 writeLine("stdout", "[[\n*cmd_stdout\n]]" )
            }
        }
    }
}

#
#  Utility functions / rules
#

kvpair_to_json(*x)  
{   
    *jstg = "{\n"
    *sep = " " 
    foreach (*n in *x) {
        *jstg = *jstg ++ '*sep "*n": "' ++ *x.*n ++ '"'
        *sep = ",\n "
    }
    *jstg = *jstg ++ "\n}"
    *jstg
}

full_application_name_from_glob (*app_sel, *app_lst)
{
   *app_path = ""
   msiSubstr(*app_sel, '0', '2' , *first2)
   if (*first2 == '*/') {
       foreach( *x in *app_lst) { 
           if (*x like *app_sel)  { *app_path = *x; break; }
       }
   }
   *app_path 
}


application_context_from_input ( *host, *context, *input_coll_pattern, *input_data_basename)
{
    *x.compute_host = ""
    foreach ( *d in select COLL_NAME, DATA_NAME, RESC_LOC ,RESC_NAME
                     where COLL_NAME like '*input_coll_pattern'
                     and   DATA_NAME = '*input_data_basename')
    {
        *x.compute_host = *d.RESC_LOC
        *x.compute_resource = *d.RESC_NAME
        *x.input_collection_hint = *d.COLL_NAME
        *x.Env__data_set = *d.DATA_NAME 
        *host = *x.compute_host
        *context = kvpair_to_json ( *x )
        break
    }
}


INPUT  *data="a.img.csv", *incoll="%", *outcoll=$"/tempZone/home/alice/output", *app=$"*/sobel_notebook.json", *wait_secs=5
OUTPUT ruleExecOut
