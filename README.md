# Driver Drowsiness Detection System

This project implements a real-time driver drowsiness detection system using two methods:

- YOLOv8 (Deep Learning-based Eye-State Classification)
- EAR (Eye Aspect Ratio using MediaPipe FaceMesh)

The goal is to detect early signs of drowsiness in drivers and trigger timely alerts, with a focus on real-time performance and CPU-only deployment.

## Project Structure

Dataset_A_Eye_Images/ # Original CEW dataset (unlabeled)
yolo_dataset/ # Annotated dataset (VOC format)
Drowsiness using YOLOv8/ # YOLOv8 model training and testing
Drowsiness using EAR/ # EAR-based real-time detection
README.md

## Features

- Trained YOLOv8n model for open/closed eye classification
- Manual annotation of 9000+ eye images using bounding boxes
- Real-time EAR detection system using MediaPipe FaceMesh
- 30 FPS processing using only CPU
- Stabilization using tessellation to handle camera shaking
- Flask-based web application for real-time detection
- Visual display of EAR graph and landmark tracking

## Methodology

### YOLOv8 Approach

- Dataset annotated with two classes: `open_eye` and `closed_eye`
- Trained using YOLOv8n (nano variant) on 160x160 input size
- Achieved:
  - mAP50: 97.8%
  - Closed eye precision: 90.7%
  - Frame rate: 5 FPS (GPU required)

### EAR Approach

- Used MediaPipe FaceMesh to locate 6 points per eye
- EAR formula:
  EAR = (||P1-P2|| + ||P3-P4||) / (2 \* ||P5-P6||)

- Real-time EAR calculated every frame and smoothed over 50 frames
- Alert triggered if EAR < 0.20 for 50 consecutive frames
- Achieved:
- 89% accuracy in normal light
- 8% accuracy drop in low-light
- 30 FPS with no GPU

## Web Application

A lightweight Flask web application was developed to provide browser-based monitoring using the EAR method.

- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask)
- Features:
- Live camera feed
- Visual landmarks
- EAR graph (live plot)

---

## How to Run the Web Application

1. **Go to the `4. Drowsiness using EAR -> Web Application -> app.py`** where the Flask app code is located.

2. **Install required libraries** (if not already installed):
   `pip install flask opencv-python mediapipe`

3. **Run the Flask server**:
   `python app.py`

4. **Open your browser** and go to:
   `http://127.0.0.1:5000/`

5. You will see:

- Live webcam feed
- Real-time EAR graph
- Landmarks on the eyes
- Drowsiness alerts if EAR drops below threshold

Make sure your webcam is connected and accessible. The app is optimized for Chrome.

---

## Sample Results

| Class      | Precision | Recall | mAP50 |
| ---------- | --------- | ------ | ----- |
| closed_eye | 0.907     | 0.898  | 0.963 |
| open_eye   | 0.974     | 0.969  | 0.992 |

## Future Work

- Add yawn detection using MAR (Mouth Aspect Ratio)
- Improve low-light performance with infrared camera
- Deploy full solution on Raspberry Pi (camera + buzzer + battery)
- Combine YOLOv8 for personalization with EAR for runtime monitoring

## References

1. Soukupová, K., & Čech, J. (2016). Real-Time Eye Blink Detection Using Facial Landmarks. Computer Vision Winter Workshop. Available: https://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf
2. Weng, W., Hsieh, Y., & Chen, M. Driver Drowsiness Detection Dataset (DDD). National Tsing Hua University. Available: http://cv.cs.nthu.edu.tw/php/callforpaper/datasets/DDD/
3. Yadav, B. S. (2021). Design and Development of Driver Drowsiness Detection System. Master’s Thesis, Florida Institute of Technology. Available: https://repository.fit.edu/cgi/viewcontent.cgi?article=1768&context=etd
4. Orenjix. CEW Dataset: A Eye. Kaggle. Available: https://www.kaggle.com/datasets/orenjix/cew-dataset-a-eye
5. Tan, X. Closed Eye Databases. NUAA. Available: https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/xtan/ClosedEyeDatabases.html
6. GeeksforGeeks. Python OpenCV | cv2.putText() Method. Available: https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/
7. Google AI. Face Landmarker in Python (MediaPipe). Available: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/python#live-stream
8. Google Developers. ML Kit Face Mesh Detection: Concepts. Available: https://developers.google.com/ml-kit/vision/face-mesh-detection/concepts

## Image Credits

- Close-up eye photo used in visualizations:  
  Marina Vitale on Unsplash – https://unsplash.com/photos/persons-blue-eyes-in-close-up-photography-Z-5i0RVukdU

## Author

**Hemin Shah**  
Graduate Student, University of Regina  
Email: `hsm002@uregina.ca`
