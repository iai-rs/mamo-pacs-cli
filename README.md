In `/ranking-model` there are files needed for creating the docker image for running ranking model on folder `/ranking-model/data` and writting results in the postgres database.

On the NTP server there is already supposed to be some version of image named `ranking-model` which could be useful, as building for some reason takes >30min. 

If not, build the image by running `docker build -t ranking-model .` from `/ranking-model`.

After building, download the model from [here](https://drive.google.com/file/d/0B1PVLadG_dCKN0ZxNFdCRWxHRFU/view?usp=drive_link&resourcekey=0-nIR7ah5t0EUVPCxuGJbW9Q) and paste in the root of the container.

Inside the container set the folowing environment variables: 

export DB_USERNAME=...<br>
export DB_PASSWORD=...<br>
export DB_HOSTNAME=...<br>
export DB_PORT=...<br>
export DB_NAME=...<br>

Model and environment variables should already be set in the container already running on NTP named `mammo-ranking`. The `/data` inside this container contains sample images from InBreast open dataset.

From the container, run `python main.py` and the model will be ran and the results will be written to the DB.
