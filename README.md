# 🩺 PneumoScan  
AI-powered web app that detects Pneumonia from chest X-ray images using a CNN + AdaBoost hybrid model.  
Built with **Django**, **TensorFlow**, and **scikit-learn**.

---

## 🚀 Features
- Upload chest X-ray images
- Deep-learning–based infection detection
- Pneumonia / Normal classification
- Confidence score
- Clean and modern UI
- Auto-save predictions to database

---

## 🧠 Tech Stack
- **Backend:** Django, Python
- **AI Models:** TensorFlow/Keras CNN + AdaBoost
- **Frontend:** HTML, CSS, Bootstrap UI
- **Database:** SQLite (default)

---

## 🖥 How to Run Locally
git clone 

cd PneumoScan

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py runserver

---

## 📁 Project Structure
detector/        → Django project
predict/         → App with UI + prediction logic
models/          → AI model files (cnn_model.h5, booster.pkl)
media/           → Uploaded X-ray images
static/          → CSS + JS


---
## 📌 Model Files Not Included

This project requires trained machine learning model files:
models/
 ├── cnn_model.h5
 └── booster.pkl
 These files are not included in the GitHub repository because:
	•	Model files are large
	•	They are created during training
	•	GitHub is not meant for storing ML models

  ## 🔽 How to run the project:
  
	1.	Download the model files from this link:
👉  (https://drive.google.com/uc?export=download&id=1YLDd4MPwJFlWNfCJsWCFY0jqT7URNGPW)
	2.	Place them inside the models/ folder in the project directory
	3.	Run the project normally:
    python manage.py runserver

## ⚠️ Disclaimer
This project is for **educational/research purposes only**  
and **not intended for clinical diagnosis**.

---

## 📬 Contact
**Author:** Aditya Gupta  
Feel free to open issues or contribute!
