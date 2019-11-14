#
# Configuration:
#

SLURM_COLLECTION_INIT='~/.slurm'

#
# Accessor/creator function:
#

slurm_collection ()
{
    local INIT=${SLURM_COLLECTION_INIT}
    local IPWD_OUT=$( # -- don't icd in current shell
        if [ -n "$INIT" ]; then
            if [[ $INIT = /?* ]]; then # -- absolute path
                icd "$INIT"
            else
                ## if path is non-absolute, then take as relative to home collection
                { icd && icd "$INIT" ; } || { imkdir -p "$INIT" && icd "$INIT" ; }
            fi
        else
            icd      # -- if blank or undefined, then default to home collection
        fi >/dev/null 2>&1
        ipwd
    )
    echo "$IPWD_OUT"
}

: ${SLURM_COLLECTION:=$(slurm_collection)}
export SLURM_COLLECTION
