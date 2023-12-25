# Criminal-Detection-Using-FRS-SSIP-Hackathon-Project_version-1.0.1
This project is project of SSIP New India Vibrant Hackathon Grand Final. It's a project on Criminal Detection using Facial Recognition System.

## Introduction
This project is developed using Python, HTML, CSS, JS & Firebase. We have extracted weapon database from official CBI Website. The weapon dataset is taken from google images.

## Use
- ```
  git clone https://github.com/rohan-shaw/Criminal-Detection-Using-FRS-SSIP-Hackathon-Project_version-1.0.1.git
  ```
- ```
  cd Criminal-Detection-Using-FRS-SSIP-Hackathon-Project_version-1.0.1
  ```
- Run
  ```
  pip install -r requirements.txt
  ```
- Add `key.json` with your firebase project json file
- Add .env file with `SECRET_KEY`, `DATABASE_URL`, `STORAGE_BUCKET`
- Run
  ```
  python train-autho.py
  ```
- Run
  ```
  python train-data.py
  ```
- Run
  ```
  python app.py
  ```
- The project is now running on your host address on port `3000`
