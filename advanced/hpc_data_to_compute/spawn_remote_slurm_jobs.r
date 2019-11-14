main_rule
{
    *host = host_for_resource_role ( *key, *val )
    writeLine ("stdout", "host=[*host]")
    if (*host == "") {
        writeLine("stderr", "null host - please define COMPUTE_RESOURCE_ROLE metadata")
    }
    else {
        remote(*host, "") {
            msiExecCmd("submit_thumbnail_jobs.py","--input '*default_input'",
                       "null","null","null", *OUT)
        }
    }
}

host_for_resource_role (*key, *value)
{
    *host = ""
    foreach (*h in select RESC_LOC where META_RESC_ATTR_NAME = '*key'
                                     and META_RESC_ATTR_VALUE = '*val')
    {
        *host = *h.RESC_LOC
    }
    *host
}

INPUT *default_input="/$rodsZoneClient/home/$userNameClient/stickers.jpg", *key="COMPUTE_RESOURCE_ROLE", *val="IMAGE_PROCESSING"
OUTPUT ruleExecOut
