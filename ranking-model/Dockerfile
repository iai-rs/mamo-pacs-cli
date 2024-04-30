FROM python:3.6.15

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y #required for open-cv
COPY . .
RUN pip install -r requirements.txt

