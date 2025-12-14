import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-water-app'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///water.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SPIKE_DETECTION_THRESHOLD = 1.5
    SPIKE_DETECTION_WINDOW = 7
