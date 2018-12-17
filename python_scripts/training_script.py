import csv
import sys
import numpy as np
import time
from sklearn.externals import joblib
import argparse
from sklearn.ensemble import ExtraTreesClassifier

csv.field_size_limit(sys.maxsize)


def load_data(path_name, n_rows, n_cols):

    count = 0
    X = np.zeros((n_rows, n_cols), dtype=np.float)
    y = np.zeros(n_rows, dtype=np.uint8)
    pai_id = np.zeros(n_rows, dtype=np.uint8)

    with open(path_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            x = np.fromstring(row[0], dtype=np.float, sep=' ')
            X[count] = x
            y[count] = int(row[1])
            pai_id[count] = int(row[2])
            count += 1
            if count >= N_ROWS:
                break

    return X, y, pai_id


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--name", required=True, help="name of trained model")
    ap.add_argument("-i", "--csv_file_to_train", required=True, help="input csv file to train the classifier")
    ap.add_argument("-f", "--folder_to_store_classifier", required=True, help="directory to store the trained classifier")
    ap.add_argument("-r", "--rows", required=True, help="total number of rows in the csv file")
    ap.add_argument("-c", "--cols", required=True, help="dimension of the feature vector")
    args = vars(ap.parse_args())

    N_ROWS = int(args["rows"])  # Total number of rows in csv file
    N_COLS = int(args["cols"])  # Dimension of the Feature Vector
    training_file = args["csv_file_to_train"]  # Input csv file with the training data
    output_folder = args["folder_to_store_classifier"]  # Directory to store the trained classifier

    # # LOAD DATA
    X_train, y_train, PAI_ID = load_data(training_file, N_ROWS, N_COLS)

    # Random Forest CLASSIFIER
    print "Training data ETC"
    clf = ExtraTreesClassifier(n_estimators=20, min_samples_leaf=10, n_jobs=8)
    start_time = time.time()
    clf.fit(X_train, y_train)
    elapsed_time = time.time() - start_time
    print "ExtraTreesClassifier %.3f s" % elapsed_time
    joblib.dump(clf, output_folder + args["name"] + "_extraTreesClassifier" + '.pkl')
    print "Generated:", output_folder + args["name"] + "_extraTreesClassifier" + '.pkl'
