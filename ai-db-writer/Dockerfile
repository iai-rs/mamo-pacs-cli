FROM python:3.12.4

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 openconnect  -y #required for open-cv
COPY ./requirements.txt ./requirements.txt 
RUN pip install -r requirements.txt
RUN yes | apt-get install vim

# ENV DB_USERNAME=postgres \
    # DB_PASSWORD=ai-mambo \
    # DB_HOSTNAME=ai-mambo-docker \
    # DB_PORT=5432 \
    # DB_NAME=postgres \
    # MINIO_HOST=minio-server \
    # MINIO_PORT=9000

COPY . .
ENTRYPOINT ./vpn.sh
