# imports
import numpy as np
from cellpose import models, core, io, plot, train
from pathlib import Path
from tqdm import trange
import matplotlib.pyplot as plt

io.logger_setup() # run this to get printing of progress

train_dir = "/mnt/WorkingDos/cellpose_sam/8_hdrg_jayden_dataset_data"
model_name = "cp_sam_hdrg_topoint_model"

def train_cp_sam_model(train_dir, model_name, n_epochs=100, learning_rate=1e-5, weight_decay=0.1, batch_size=1):
  """
  Train a Cellpose model using the SAM (Segment Anything) algorithm.

  Args:
    train_dir (str): Path to the directory containing the training data.
    model_name (str): Name of the model to be trained.
    n_epochs (int): Number of epochs to train the model.
    learning_rate (float): Learning rate for the optimizer.
    weight_decay (float): Weight decay for the optimizer.
    batch_size (int): Batch size for training.

  Returns:
    None
    """
  # Check if colab notebook instance has GPU access
  if core.use_gpu()==False:raise ImportError("No GPU access, change your runtime")

  model = models.CellposeModel(gpu=True)

  if not Path(train_dir).exists():raise FileNotFoundError("directory does not exist")

  test_dir = None # optionally you can specify a directory with test files

  # *** change to your mask extension ***
  # masks_ext = "_seg.npy"
  # ^ assumes images from Cellpose GUI, if labels are tiffs, then "_masks.tif"

  # list all files
  masks_ext = "_masks"
  files = [f for f in Path(train_dir).glob("*") if "_masks" not in f.name and "_flows" not in f.name and "_seg" not in f.name]

  if(len(files)==0):raise FileNotFoundError("no files found, did you specify the correct folder and extension?")
  else:print(f"{len(files)} files in folder:")

  output = io.load_train_test_data(train_dir, test_dir, mask_filter=masks_ext)
  train_data, train_labels, _, test_data, test_labels, _ = output
  new_model_path, train_losses, test_losses = train.train_seg(model.net, train_data=train_data, train_labels=train_labels, batch_size=batch_size, n_epochs=n_epochs, learning_rate=learning_rate, weight_decay=weight_decay, nimg_per_epoch=max(2, len(train_data)), model_name=model_name)


if __name__ == "__main__":
  train_cp_sam_model(train_dir, model_name, n_epochs, learning_rate, weight_decay, batch_size)