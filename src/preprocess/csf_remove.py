import os
from nipype.interfaces import fsl
from nipype.interfaces.io import DataSink
from nipype.pipeline.engine import Node, Workflow

# Define the workflow
wf = Workflow(name="csf_segmentation")
wf.base_dir = os.path.abspath('./csf_workflow')

# Input MRI file (T1-weighted)
input_file = "/mnt/storage/ji/TEMP/images/train/T1_sub-101.nii.gz"  # Replace with your MRI file path

# Node for bias field correction
bias_correct = Node(fsl.FAST(), name="bias_correction")
bias_correct.inputs.in_files = input_file
bias_correct.inputs.bias_iters = 3
bias_correct.inputs.output_biascorrected = True

# Node for tissue segmentation (CSF, GM, WM)
segment = Node(fsl.FAST(), name="segmentation")
segment.inputs.number_classes = 3  # 3 tissue types: CSF, GM, WM
segment.inputs.output_type = 'NIFTI_GZ'

# Connect the output of bias correction to segmentation
wf.connect(bias_correct, "restored_image", segment, "in_files")

# Data sink to save the results
datasink = Node(DataSink(), name='datasink')
datasink.inputs.base_directory = os.path.abspath('./csf_results')

# Connect segmentation outputs to datasink
wf.connect(segment, "partial_volume_files", datasink, "segmentation.@partial_volumes")
wf.connect(segment, "tissue_class_files", datasink, "segmentation.@tissue_classes")

# Run the workflow
wf.run()

# The CSF segmentation will be in the first tissue class file (index 0)
print("CSF segmentation completed. Results saved in ./csf_results")
print("CSF segmentation is in the first tissue class file (index 0) or partial volume file")