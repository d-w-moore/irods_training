testRule 
{
  *thumbnail_sizes = "128x128,256x256,512x512,1024x1024" 

  *host = ""
  *key = "COMPUTE_RESOURCE_ROLE"; *val="IMAGE_PROCESSING"

  *image_compute_resc = ""
  get_host_and_resource_name_by_role(*host, *image_compute_resc, *key, *val) 

  *key = "COMPUTE_RESOURCE_ROLE"; *val_LTS="LONG_TERM_STORAGE"
  *long_term_storage_resc = ""
  get_resource_name_by_role( *long_term_storage_resc, *key, *val_LTS )

  writeLine ("stdout", "host=[*host] image compute resc =[*image_compute_resc]")
  writeLine ("stdout", "---- long term storage resc=[*long_term_storage_resc]")
  writeLine ("stdout", "thumbnails to generate : [ *thumbnail_sizes ]")

  *input_file_name = "stickers"
  *input_file_ext = ".jpg"
  *input_file =  "*input_file_name" ++ "*input_file_ext"

  if ("*host" == "") {

    writeLine ("stdout", "Host for job launch was not found.")

  } else {

    *src_phy_path = "null"

    foreach (*x in select DATA_PATH where 
    # COLL_NAME = '/tempZone/home/*user' and
      DATA_NAME = '*input_file' and RESC_NAME = '*image_compute_resc') 
    {
      *src_phy_path = *x.DATA_PATH
    }

    *src_phy_dir = trimr ("*src_phy_path", "/")

    remote(*host, "") {

      *collection_out = "*input_file_name" ++ "_thumbnails"
      *tmpdir = "/tmp/irods/thumbnails"

      *user = ""
      get_irods_username(*user)

      if (*user != '') {
        foreach (*size in split (*thumbnail_sizes, ",")) {

          *output_file =  "*input_file_name" ++ "_*size" ++ "*input_file_ext"

          # - parameters & input/output directories for thumbnail compute container
          *container_opts = "exec thumbnail_image " ++
                            "--resc_for_bind '*image_compute_resc' " ++
                            "--bind *src_phy_dir/:/src --bind *tmpdir/:/dst " ++ 
                            " /usr/bin/python3 /make_thumbnail.py " ++
                            " *size *input_file *output_file " ++ 
                            "/tempZone/home/*user/*collection_out "

          # - location & parameters for intermediate products
          *interface_opts = "--outdir *tmpdir" 

          # - parameters & mdmanifest location for metadata application
          *postproc_opts = "-r *image_compute_resc -f *long_term_storage_resc " ++
                           "-p *tmpdir/stickers_*size.jpg " ++
                           "-m *tmpdir/" ++ "*size" ++ "_mdmanifest.json"

          rmtExec_singularity("*container_opts","*interface_opts",
                              "*postproc_opts")

        } #foreach
      } #if (*user != '') 

    } #remote

  } #if-else

} # end rule

INPUT  null
OUTPUT ruleExecOut
