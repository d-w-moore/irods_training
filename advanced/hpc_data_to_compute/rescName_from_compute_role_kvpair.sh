#!/bin/sh
if [ $# -lt 2 ] ; then
  echo >&2 "iRODS Data To Compute training -- resource query utility"
  echo >&2 "  (Look up resource name in ICAT by compute-related role key/value)"
  echo >&2 "example uses: $0  'COMPUTE_RESOURCE_ROLE'  'IMAGE_PROCESSING'"
  echo >&2 "              $0  'COMPUTE_RESOURCE_ROLE'  'LONG_TERM_STORAGE'"
  exit 1
fi
RESC_NAME=$( iquest '%s' "select RESC_NAME where  META_RESC_ATTR_NAME = '$1' and META_RESC_ATTR_VALUE = '$2' ")
echo "$RESC_NAME"
