# VALDO_brain_MRI_dataset_preprocessing

## Setup for Skull Stripping
- The SynthStrip, skull stripping module, needs to be installed. <URL> https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/
- environtment variable needs to be defined \
`export FREESURFER_HOME= #The directory that 'freesurfer' is located` \
`source $FREESURFER_HOME/SetUpFreeSurfer.sh`

## FSL
export FSLDIR=/media/Datacenter_storage/Ji/fsl

source $FSLDIR/etc/fslconf/fsl.sh


## ANT
`git clone https://github.com/ANTsX/ANTs.git`

```python
workingDir=${PWD}
git clone https://github.com/ANTsX/ANTs.git
mkdir build install
cd build
cmake \
    -DCMAKE_INSTALL_PREFIX=${workingDir}/install \
    -DBUILD_TESTING=OFF \
    -DRUN_LONG_TESTS=OFF \
    -DRUN_SHORT_TESTS=OFF \
    ../ANTs 2>&1 | tee cmake.log
make -j 4 2>&1 | tee build.log
cd ANTS-build
make install 2>&1 | tee install.log
```
