from cellpose import io, models, train
io.logger_setup()

output = io.load_train_test_data(train_dir, test_dir, image_filter="_img", mask_filter="_masks", look_one_level_down=False)
images, labels, image_names, test_images, test_labels, image_names_test = output
model = models.CellposeModel(gpu=True)

model_path, train_losses, test_losses = train.train_seg(model.net, train_data=images, train_labels=labels, test_data=test_images, test_labels=test_labels, weight_decay=0.1, learning_rate=1e-5, n_epochs=100, model_name="my_new_model")

# training
# python -m cellpose --train --dir /Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/train
# --learning_rate 0.00001 --weight_decay 0.1 --n_epochs 100 --train_batch_size 1

# python -m cellpose \
#   --train \
#   --dir /Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/train_old \
#   --learning_rate 1e-5 \
#   --weight_decay 0.1 \
#   --n_epochs 100 \
#   --batch_size 1 \
#   --verbose


# python -m cellpose \
#   --train \
#   --dir /Users/discovery/Downloads/xenium_testing_jit/spinal_cord_samples_fr/train \
#   --learning_rate 1e-5 \
#   --weight_decay 0.1 \
#   --n_epochs 100 \
#   --batch_size 1 \
#   --verbose