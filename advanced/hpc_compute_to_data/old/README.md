
Compute to Data - main steps
------

Data is automatically routed based on rules

- data routing operation is simulated in the exercise by a put

- in the exercise 

  * alice will put the stickers.jpg file to be processed
  * run a rule-file client side to launch the desired containers on the HPC ("remote") side
  * wait for the appropriate delay (usually < 5 secs) to see result via "cd ; ils -l stickers_thumbnails"
      
 - on the HPC side, this is what happens:
  * remote call to containers launched on HPC, where rods admin acts on behalf of client to
    run two containers:
    
    1. **thumbnail_image**
    
      - docker image run by Singularity
      - filesystem operations only 
      - generate thumbnail and metadata manifest
      
    2. **metadata_addtags**
    
      - Singularity container running a proxy-as-user-on-PRC Singularity build
      - picks up a $SIZE_STRING-mdmanifest.json, to add the metadata tags to the output
      - register the products (thumbnail images) and attach the metadata from the last step
      - replicate thumbnails to long term storage and trim from HPC scratch storage
