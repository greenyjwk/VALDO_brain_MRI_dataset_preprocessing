# brain MRI Preprocessing(VALDO Dataset/Mayo Dataset)

## Setup for Skull Stripping
- The SynthStrip, skull stripping module, needs to be installed. <URL> https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/
- Instructino Guide: https://surfer.nmr.mgh.harvard.edu/fswiki/rel6downloads
- environtment variable needs to be defined \

 
`tar -C /usr/local -xzvf freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz` \
`export FREESURFER_HOME= #The directory that 'freesurfer' is located` \
`source $FREESURFER_HOME/SetUpFreeSurfer.sh`

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

or
just simply install on the conda environment
`conda install aramislab::ants`
