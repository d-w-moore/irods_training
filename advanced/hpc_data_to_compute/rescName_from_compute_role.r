get_resource_name_from_COMPUTE_RESOURCE_ROLE
{
    *resc_name = ""
    foreach(*row in SELECT DATA_RESC_NAME WHERE META_RESC_ATTR_NAME = '*role_name' AND 
                    META_RESC_ATTR_VALUE = '*role_value') 
    {
        *resc_name = *row.DATA_RESC_NAME
    }
    writeLine("stdout", "*resc_name")
}

INPUT  *role_name="COMPUTE_RESOURCE_ROLE", *role_value=$"IMAGE_PROCESSING"
OUTPUT ruleExecOut
