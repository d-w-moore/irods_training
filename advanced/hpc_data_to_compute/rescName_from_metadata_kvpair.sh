#!/bin/sh
RESC_NAME=$( iquest '%s' "select RESC_NAME where  META_RESC_ATTR_NAME = 'COMPUTE_RESOURCE_ROLE' and META_RESC_ATTR_VALUE = '$1' ")
echo "$RESC_NAME"
