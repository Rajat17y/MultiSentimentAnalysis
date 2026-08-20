# SentimentScope

### Detecting Realtime Sentiment Gaps Across Social Media

SentimentScope is a real-time sentiment analysis platform designed to detect and compare sentiment trends across multiple social media and developer platforms.

The system collects publicly available posts and comments from **Reddit, YouTube, HackerNews, and Dev.to** using custom data collection pipelines. The collected data is processed through a preprocessing pipeline that handles **label normalization, negation handling, text cleaning, and class imbalance**.

For sentiment classification, the project uses a **BiLSTM + Attention deep learning model built with TensorFlow/Keras**, trained on more than **2.86 million samples**. The model achieved **76.13% test accuracy** and a **0.73 macro-averaged F1 score** across three sentiment classes: **Positive, Neutral, and Negative**.

The trained model is deployed as a **Django web application** with a live dashboard that allows users to enter a topic and analyze sentiment across different platforms.

---

## Features

* 🌐 Multi-platform sentiment analysis

  * Reddit
  * YouTube
  * HackerNews
  * Dev.to
* 🔍 Topic-based sentiment analysis
* 🧹 Text preprocessing and normalization
* 🧠 BiLSTM + Attention deep learning model
* 📊 Three-class sentiment classification:

  * Positive
  * Neutral
  * Negative
* 📈 Platform-wise sentiment comparison
* 🎯 Prediction confidence for individual comments/posts
* ⚡ Real-time analysis pipeline
* 🌐 Django-based web application
* 📊 Interactive sentiment dashboard
* 💾 Storage of analysis results using Django's database layer

---

# Machine Learning Model

The sentiment classification model is based on a **Bidirectional Long Short-Term Memory (BiLSTM)** network enhanced with an **Attention mechanism**.

The model was trained on a dataset containing **2.86M+ samples** collected from multiple online platforms.

### Model Performance

| Metric         |      Score |
| -------------- | ---------: |
| Test Accuracy  | **76.13%** |
| Macro F1 Score |   **0.73** |

The model predicts one of the following three sentiment classes:

```text
Positive
Neutral
Negative
```

---

# Technology Stack

## Machine Learning

* Python 3.10.11
* TensorFlow / Keras
* BiLSTM
* Attention Mechanism
* Pandas
* NumPy
* Scikit-learn
* NLTK

## Data Collection

* Reddit
* YouTube
* HackerNews
* Dev.to
* Custom scraping/data collection pipelines

## Backend

* Django
* Django REST Framework

## Frontend

* HTML
* CSS
* JavaScript
* Django Templates

## Database

* SQLite / Django-supported database

---

# Project Architecture

The overall workflow of SentimentScope can be summarized as:

```text
                    User
                     │
                     ▼
             Enter Analysis Topic
                     │
                     ▼
              Django Application
                     │
                     ▼
             Data Collection Layer
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
       Reddit     YouTube    HackerNews
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
                  Dev.to
                     │
                     ▼
             Text Preprocessing
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
       Cleaning  Normalization  Negation
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
             BiLSTM + Attention
                     │
                     ▼
             Sentiment Prediction
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
       Positive   Neutral    Negative
                     │
                     ▼
              Django Dashboard
                     │
                     ▼
          Platform-wise Analysis
```

---

# Running the Project Locally

Follow the steps below to run SentimentScope on your local machine.

## Prerequisites

Make sure the following are installed on your system:

* **Python 3.10.11**
* **Git**
* **pip**

> **Important:** This project uses Python **3.10.11**. It is recommended to use exactly this Python version to avoid dependency and TensorFlow compatibility issues.

Verify your Python version:

```bash
python --version
```

It should display:

```text
Python 3.10.11
```

If you have multiple Python versions installed, you can check them on Windows using:

```bash
py -0
```

---

# 1. Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/Rajat17y/MultiSentimentAnalysis.git
```

Move into the cloned project:

```bash
cd MultiSentimentAnalysis
```

---

# 2. Create the Virtual Environment Outside the Project

The virtual environment should **not** be created inside the `MultiSentimentAnalysis` directory.

For example, if your folders look like this:

```text
Projects/
│
├── MultiSentimentAnalysis/
│   ├── manage.py
│   ├── requirements.txt
│   ├── ...
│
└── sentiment_env/
```

The `sentiment_env` folder is the virtual environment, while `MultiSentimentAnalysis` contains the actual project.

## Windows

First, go to the directory that contains `MultiSentimentAnalysis`:

```bash
cd ..
```

Then create the virtual environment using Python 3.10:

```bash
py -3.10 -m venv sentiment_env
```

The resulting structure will be:

```text
Parent Folder/
│
├── MultiSentimentAnalysis/
│
└── sentiment_env/
```

---

# 3. Activate the Virtual Environment

On Windows:

```bash
sentiment_env\Scripts\activate
```

After activation, your terminal should look similar to:

```text
(sentiment_env) C:\path\to\Parent Folder>
```

> Make sure `(sentiment_env)` appears at the beginning of your terminal. This indicates that the virtual environment is active.

---

# 4. Go Back to the Project

After activating the virtual environment, navigate back into the project:

```bash
cd MultiSentimentAnalysis
```

You should now be inside:

```text
MultiSentimentAnalysis/
```

while the active virtual environment remains located outside the project.

---

# 5. Install Project Dependencies

Make sure the virtual environment is active and install all required packages:

```bash
pip install -r requirements.txt
```

This will install the dependencies required by the project, including Django, TensorFlow, NLTK, Pandas, NumPy, and other required packages.

---

# 6. Configure Environment Variables

SentimentScope uses the **YouTube Data API** to collect YouTube data.

You need to create a `.env` file in the **root directory of the project**, at the same level as `manage.py`.

The project structure should look like:

```text
MultiSentimentAnalysis/
│
├── manage.py
├── requirements.txt
├── .env
├── ...
```

Create a file named:

```text
.env
```

Then add your YouTube API key:

```env
YOUTUBE_API_KEY="your_youtube_api_key"
```

Replace:

```text
your_youtube_api_key
```

with your actual YouTube Data API key.

### Getting a YouTube API Key

You can obtain a YouTube Data API key through the **Google Cloud Console** by creating/selecting a Google Cloud project and enabling the **YouTube Data API v3**.

> **Important:** Never share your API key publicly or commit your `.env` file to GitHub.

Make sure `.env` is included in your `.gitignore`:

```gitignore
.env
```

---

# 7. Download NLTK Stopwords

The project uses the NLTK `stopwords` dataset during text preprocessing.

Run:

```bash
python -m nltk.downloader stopwords
```

You only need to perform this step once for the environment.

---

# 8. Apply Django Database Migrations

Before running the application, apply the database migrations:

```bash
python manage.py migrate
```

If you want to create a Django administrator account, you can optionally run:

```bash
python manage.py createsuperuser
```

Follow the instructions shown in the terminal.

---

# 9. Run the Django Server

Start the development server:

```bash
python manage.py runserver
```

You should see something similar to:

```text
Starting development server at http://127.0.0.1:8000/
```

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

The SentimentScope application should now be running locally.

---

# Quick Setup — Windows

If Python 3.10.11 and Git are already installed, the complete setup can be performed using:

```bash
git clone https://github.com/Rajat17y/MultiSentimentAnalysis.git

cd MultiSentimentAnalysis

cd ..

py -3.10 -m venv sentiment_env

sentiment_env\Scripts\activate

cd MultiSentimentAnalysis

pip install -r requirements.txt

python -m nltk.downloader stopwords

python manage.py migrate

python manage.py runserver
```

> Before running the Django server, make sure you have created the `.env` file and added your `YOUTUBE_API_KEY`.

---

# Using the Application

Once the Django server is running:

1. Open the application in your browser.
2. Enter a topic that you want to analyze.
3. SentimentScope collects relevant data from the supported platforms.
4. The collected data goes through the preprocessing pipeline.
5. The BiLSTM + Attention model predicts the sentiment of the collected content.
6. The dashboard displays overall sentiment statistics.
7. Platform-wise sentiment can be compared.
8. Individual comments/posts can be viewed along with their predicted sentiment and confidence.

---

# Example Analysis Workflow

```text
Enter Topic
     │
     ▼
"Artificial Intelligence"
     │
     ▼
Collect Data
     │
     ├── Reddit
     ├── YouTube
     ├── HackerNews
     └── Dev.to
     │
     ▼
Preprocess Text
     │
     ▼
BiLSTM + Attention Model
     │
     ▼
Sentiment Predictions
     │
     ├── Positive
     ├── Neutral
     └── Negative
     │
     ▼
Generate Statistics
     │
     ▼
Display Dashboard
```

---

# Project Highlights

* **2.86M+ training samples**
* **76.13% test accuracy**
* **0.73 macro F1 score**
* Multi-platform sentiment analysis
* BiLSTM + Attention architecture
* Real-time topic-based analysis
* Custom data collection pipelines
* Django-based backend
* Django REST Framework integration
* Live sentiment dashboard
* Platform-wise sentiment comparison
* Sentiment confidence scores

---

# Security

This project requires a YouTube API key to access YouTube data.

Never commit sensitive credentials to GitHub.

Your `.gitignore` should contain:

```gitignore
.env
```

If you accidentally expose an API key publicly, revoke the exposed key and generate a new one through Google Cloud.

---

# Repository

The complete source code is available on GitHub:

[MultiSentimentAnalysis — GitHub Repository](https://github.com/Rajat17y/MultiSentimentAnalysis.git?utm_source=chatgpt.com)

---

# Author

**Rajat Yadaw**

SentimentScope was developed as a project for detecting and analyzing sentiment differences across multiple online platforms using **Deep Learning, Natural Language Processing, and Django**.
