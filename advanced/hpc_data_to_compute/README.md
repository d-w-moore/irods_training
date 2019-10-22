The three major steps in DATA TO COMPUTE

1. file hits landing zone
   - simulated with iput


2. landing zone rule
   - TODO - check extension (.jpg,.gif,.tif,... etc)
   - determine target host for compute, from resource metadata
   - launch thumbnail job remotely


3. hpc rule - schedules hpc job(s)
   - prolog
      * creates a flag file in iRODS to support job tracking and
        store of relevant information in metdata
   - epilog
      * registers products into catalog
      * determines target (for LTS) from resource metadata
      * replicates products to target resource
      * trims original products from HPC filesystem
