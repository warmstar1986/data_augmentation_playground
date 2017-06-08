import tensorflow as tf
from data_preparation import mnist_data
from sklearn.model_selection import train_test_split
import numpy as np
from tensorflow.contrib.learn.python.learn.estimators.linear import LinearClassifier
from sklearn.linear_model import Perceptron
import random

def load_data_set():
	dataset = mnist_data.load_mnist(reshape=True)
	train_set=dataset.train.images
	train_labels=dataset.train.labels
	test_set=dataset.validation.images
	test_labels=dataset.validation.labels
	return train_set, train_labels, test_set, test_labels

def construct_feature_col(col_num=None):
	feature_col = []
	feature_dummy = []
	feature_name_base = "pixel_"
	for col_idx in range(col_num):
		feature_col.append(tf.contrib.layers.real_valued_column(feature_name_base+str(col_idx)+"th"))
		feature_dummy.append(feature_name_base+str(col_idx)+"th")
	return feature_col, feature_dummy

def extract_for_binary(train_set=None, train_labels=None, test_set=None, test_labels=None):
	binary_indices_train = []
	binary_indices_test = []
	for i in range(len(train_set)):
		if train_labels[i] == 6 or train_labels[i] == 8:
			binary_indices_train.append(i)
	for i in range(len(test_set)):
		if test_labels[i] == 6 or test_labels[i] == 8:
			binary_indices_test.append(i)
	train_set_binary = np.take(train_set, binary_indices_train, axis=0)
	train_label_binary = np.take(train_labels, binary_indices_train)
	test_set_binary = np.take(test_set, binary_indices_test, axis=0)
	test_label_binary = np.take(test_labels, binary_indices_test)
	return train_set_binary, train_label_binary, test_set_binary, test_label_binary

def input_fn(data_set=None, labels=None, feature_col=None):
	# Creates a dictionary mapping from each continuous feature column name (k) to
	# the values of that column stored in a constant Tensor.
	feature_columns = {k_val: tf.constant(data_set[:, k_idx]) for k_idx, k_val in enumerate(feature_col)}
	label = tf.constant(labels)
	return feature_columns, label

def down_sample(data_set=None, labels=None, down_sample_num=None):
	down_sample_indices = np.random.randint(low=0, high=data_set.shape[0], size=down_sample_num)
	down_samples = np.take(data_set, down_sample_indices, axis=0)
	down_sample_labels = np.take(labels, down_sample_indices)
	return down_samples, down_sample_labels

def random_crop(batch, crop_shape, padding=None):
	batch=batch.reshape((batch.shape[0], int(np.sqrt(batch.shape[1])), int(np.sqrt(batch.shape[1]))))
	oshape = np.shape(batch[0])
	if padding:
	    oshape = (oshape[0] + 2*padding, oshape[1] + 2*padding)
	new_batch = []
	npad = ((padding, padding), (padding, padding))
	for i in range(len(batch)):
	    new_batch.append(batch[i])
	    if padding:
	        new_batch[i] = np.lib.pad(batch[i], pad_width=npad,
	                                  mode='constant', constant_values=0)
	    nh = random.randint(0, oshape[0] - crop_shape[0])
	    nw = random.randint(0, oshape[1] - crop_shape[1])
	    new_batch[i] = new_batch[i][nh:nh + crop_shape[0],
	                                nw:nw + crop_shape[1]]
	return np.array(new_batch)

if __name__ == "__main__":
	train_set, train_labels, test_set, test_labels = load_data_set()
	aug_train_set=random_crop(train_set, (28,28), padding=2)
	aug_train_set=aug_train_set.reshape(aug_train_set.shape[0], int(aug_train_set.shape[1]**2))
	new_data_set=np.concatenate((train_set,aug_train_set),axis=0)
	print(new_data_set.shape)
