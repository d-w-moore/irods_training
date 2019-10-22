#!/bin/bash

FUNCTIONS=/var/lib/irods/compute/irods_compute_functions
if [ -r $FUNCTIONS ]; then
  . $FUNCTIONS
fi

function evaluate_template {
    PYTHONPATH=$HOME/compute python -c "import common; \
    print(common.jobParamsPlusMetadata()('$1'))
    "
}

CONVERT_EXECUTABLE="/usr/bin/convert"
SRUN_OPTIONS="--nodes=1-1 --ntasks=1 --cpus-per-task=1"

if test_irods_slurm_desc ; then

  if [ "$COMPUTE_JOB_TYPE" = 'generate_thumbnails' ]
      then
          set_irods_slurm_var  "compute_job_type"       "$COMPUTE_JOB_TYPE"
          set_irods_slurm_var  "input_image_collection" "$PARAM_input_image_collection"
          set_irods_slurm_var  "input_image_name"       "$PARAM_input_image_name"
          set_irods_slurm_var  "input_image_extension"  "$PARAM_input_image_extension"
          set_irods_slurm_var  "thumbnail_size"         "$2"
          set_irods_slurm_var  "input_data_object"      "$PARAM_data_object_logical_path"
          set_irods_slurm_var  "scratch_resource_name"  "$PARAM_scratch_resource_name"
          set_irods_slurm_var  "resource_use_key"       "$PARAM_resource_use_key"

          # set_irods_slurm_var  "long_term_storage_resc" $() # - dwm - can do this in template

          output_dataobject_name=`evaluate_template THUMBNAIL_OUTPUT_DATAOBJECT`
          output_dataobject_path=`evaluate_template THUMBNAIL_OUTPUT_DATAOBJECT_FULLPATH`
          mkdir -p "$PARAM_physical_output_path"
          set . "$1" "$2" "$3" "$PARAM_physical_output_path/$output_dataobject_name"
          shift
          set_irods_slurm_var  "physical_output_dir" "$PARAM_physical_output_path"
          set_irods_slurm_var  "output_object_name" "$output_dataobject_name"
      else
          set . "$1" "$2" "$3" "$4"
          shift
      fi
fi

# Allow us time to see jobs via SLURM's squeue

sleep 4

exec srun $SRUN_OPTIONS "$CONVERT_EXECUTABLE" "$@" 
