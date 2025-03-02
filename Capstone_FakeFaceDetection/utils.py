import matplotlib
matplotlib.use("Agg")

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle
import cv2
import os
import time
from classifier.hand_crafted_model import LocalBinaryPatterns

from config import EPOCHS

def get_arguments():
	# construct the argument parser and parse the arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("--dataset", "-d", default="dataset",
		help="path to input dataset")
	parser.add_argument('--model', '-m', default='deeplearning',
		choices=['deeplearning', 'logistic_regression', 'knn', 'random_forest',
				'decision_tree', 'naive_bayes', 'svm', 'mlp'],
		help='The model for training')
	#parser.add_argument('--numPoints', '-nP', default=24,
	#	help='The number of points parameter for LBPs appoach')
	#parser.add_argument('--radius', '-r', default=8,
	#	help='The radius parameter for LBPs appoach')

	return vars(parser.parse_args())

def load_datasetDeep(dataset_path: str):
    # grab the list of images in our dataset directory, then initialize
    # the list of data (i.e., images) and class images
    print("[INFO] loading images...")
    imagePaths = list(paths.list_images(dataset_path))
    data = []
    labels = []
    fake_number = 0
    # loop over all image paths
    for imagePath in imagePaths:
    	# extract the class label from the filename, load the image and
    	# resize it to be a fixed 32x32 pixels, ignoring aspect ratio
       label = imagePath.split(os.path.sep)[3]
       image = cv2.imread(imagePath)
       image = cv2.resize(image, (64, 64))
       data.append(image)
       labels.append(label)
       if label == 'fake':
           fake_number += 1

    # encode the labels (which are currently strings) as integers and then
    # one-hot encode them
    print("--> The number of images: {}".format(len(labels)))
    print("\t--> The number of fake image: {}".format(fake_number))
    print("\t--> The number of real image: {}".format(len(labels)-fake_number))
    time.sleep(3)
    le = LabelEncoder()
    labels = le.fit_transform(labels)
    labels = to_categorical(labels, 2)
    return np.array(data), np.array(labels), le


def load_datasetLBPs(dataset_path, numPoints, radius):
    # Create a LocalBinaryPatterns object
    desc = LocalBinaryPatterns(numPoints, radius)
    data = []
    labels = []
    # loop over the training image
    for imagePath in paths.list_images(dataset_path):
    # load the image, convert it to grayscale, and describe it
        image = cv2.imread(imagePath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = desc.describe(gray)
        # extract the label from the image path, then update the
        # label and data lists
        labels.append(imagePath.split(os.path.sep)[3])
        data.append(hist)
    print("--> The number of image: {}".format(len(labels)))
    time.sleep(3)
    return np.array(data), np.array(labels)


def load_extracted_feature(path):
	try:
		print("[INFO] Loading feature vectors ...")
		with open(path, 'rb') as f:
			data, labels = pickle.load(f)
	except:
		print("The path of extracted feature is not invalid !")
		exit(0)
	print("--> The number of feature vectors: {}".format(len(labels)))
	#print("\t--> The number of fake image: {}".format(len(np.array(labels)=0)))
	fake_number = 0
	for label in labels:
		if label == 'fake':
			fake_number += 1
	print("\t--> The number of fake face: {}".format(fake_number))
	print("\t--> The number of real face: {}".format(len(labels) - fake_number))
	time.sleep(3)
	return data, labels



def plot_progress(model: object, name):
    # plot the training loss and accuracy
    plt.style.use("ggplot")
    plt.figure()
    plt.plot(np.arange(0, EPOCHS), model.history["loss"], label="train_loss")
    plt.plot(np.arange(0, EPOCHS), model.history["val_loss"], label="val_loss")
    plt.plot(np.arange(0, EPOCHS), model.history["accuracy"], label="train_acc")
    plt.plot(np.arange(0, EPOCHS), model.history["val_accuracy"], label="val_acc")
    plt.title("Training Loss and Accuracy on Dataset")
    plt.xlabel("Epoch #")
    plt.ylabel("Loss/Accuracy")
    plt.legend(loc="lower left")
    if not os.path.exists("figures"):
        os.mkdir("figures")
    plt.savefig("figures/plot_" + name)
