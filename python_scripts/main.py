import numpy as np
import cv2
from sklearn.externals import joblib
import argparse
# from time import gmtime, strftime


def detect_face(img, faceCascade):
    faces = faceCascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=(110, 110)
        #flags = cv2.CV_HAAR_SCALE_IMAGE
    )
    return faces


def calc_hist(img):
    histogram = [0] * 3
    for j in range(3):
        histr = cv2.calcHist([img], [j], None, [256], [0, 256])
        histr *= 255.0 / histr.max()
        histogram[j] = histr
    return np.array(histogram)


ap = argparse.ArgumentParser()
ap.add_argument("-n", "--name", required=True, help="name of trained model to perform spoofing detection")
ap.add_argument("-d", "--device", required=True, help="camera identifier/video to acquire the image")
ap.add_argument("-t", "--threshold", required=False, help="threshold used for the classifier to decide between genuine and a spoof attack")
args = vars(ap.parse_args())

if __name__ == "__main__":

    # # Load model
    clf = None
    try:
        clf = joblib.load(args["name"])
    except IOError as e:
        print "Error loading model <"+args["name"]+">: {0}".format(e.strerror)
        exit(0)

    # # Open the camera
    if '.' in args["device"]:
        cap = cv2.VideoCapture(args["device"])
    else:
        cap = cv2.VideoCapture(int(args["device"]))
    if not cap.isOpened():
        print "Error opening camera"
        exit(0)

    width = 320
    height = 240
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

    # # Initialize face detector
    cascPath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)

    sample_number = 1
    count = 0
    measures = np.zeros(sample_number, dtype=np.float)

    while True:
        ret, img_bgr = cap.read()
        if ret is False:
            print "Error grabbing frame from camera"
            break

        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        faces = detect_face(img_gray, faceCascade)

        measures[count%sample_number]=0

        point = (0,0)
        for i, (x, y, w, h) in enumerate(faces):

            roi = img_bgr[y:y+h, x:x+w]

            img_ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCR_CB)
            img_luv = cv2.cvtColor(roi, cv2.COLOR_BGR2LUV)

            ycrcb_hist = calc_hist(img_ycrcb)
            luv_hist = calc_hist(img_luv)

            feature_vector = np.append(ycrcb_hist.ravel(), luv_hist.ravel())
            feature_vector = feature_vector.reshape(1, len(feature_vector))

            prediction = clf.predict_proba(feature_vector)
            prob = prediction[0][1]

            measures[count % sample_number] = prob

            cv2.rectangle(img_bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)

            point = (x, y-5)

            print measures, np.mean(measures)
            if 0 not in measures:
                text = "True"
                if np.mean(measures) >= 0.7:
                    text = "False"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img=img_bgr, text=text, org=point, fontFace=font, fontScale=0.9, color=(0, 0, 255),
                                thickness=2, lineType=cv2.LINE_AA)
                else:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img=img_bgr, text=text, org=point, fontFace=font, fontScale=0.9,
                                color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        count+=1
        cv2.imshow('img_rgb', img_bgr)

        key = cv2.waitKey(1)
        if key & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
