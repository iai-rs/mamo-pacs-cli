#!/bin/bash

storescp_port=55613
dicom_directory=/home/baltic/TMP_DIR_FOR_DICOMS
logs_directory=/home/baltic/cron_logs
datetime=$(date '+%Y-%m-%d-%H-%M-%S')
logfile="$logs_directory/$datetime.txt"
makefile=/home/baltic/mamo-pacs-cli/

touch $logfile
exec > $logfile 2>&1

echo "Starting ai-cron script..."

vpn_user=""
vpn_password=""
vpn_ip_address=""
vpn_psk=""
db_username=""
db_password=""
db_hostname=""
db_port=""
db_name=""
minio_host=""
minio_port=""
oci_key_content=""
oci_user=""
oci_fingerprint=""
oci_tenancy=""
ite_vpn_url=""
ite_vpn_user=""
ite_vpn_password=""

# Parse arguments
for arg in "$@"
do
  case $arg in
    vpn_user=*)
      vpn_user="${arg#*=}"
      ;;
    vpn_password=*)
      vpn_password="${arg#*=}"
      ;;
    vpn_ip_address=*)
      vpn_ip_address="${arg#*=}"
      ;;
    vpn_psk=*)
      vpn_psk="${arg#*=}"
      ;;
    db_username=*)
      db_username="${arg#*=}"
      ;;
    db_password=*)
      db_password="${arg#*=}"
      ;;
    db_hostname=*)
      db_hostname="${arg#*=}"
      ;;
    db_port=*)
      db_port="${arg#*=}"
      ;;
    db_name=*)
      db_name="${arg#*=}"
      ;;
    minio_host=*)
      minio_host="${arg#*=}"
      ;;
    minio_port=*)
      minio_port="${arg#*=}"
      ;;
    oci_key_content=*)
      oci_key_content="${arg#*=}"
      ;;
    oci_user=*)
      oci_user="${arg#*=}"
      ;;
    oci_fingerprint=*)
      oci_fingerprint="${arg#*=}"
      ;;
    oci_tenancy=*)
      oci_tenancy="${arg#*=}"
      ;;
    ite_vpn_url=*)
      ite_vpn_url="${arg#*=}"
      ;;
    ite_vpn_user=*)
      ite_vpn_user="${arg#*=}"
      ;;
    ite_vpn_password=*)
      ite_vpn_password="${arg#*=}"
      ;;
    ite_db_username=*)
      ite_db_username="${arg#*=}"
      ;;
    ite_db_password=*)
      ite_db_password="${arg#*=}"
      ;;
    ite_db_hostname=*)
      ite_db_hostname="${arg#*=}"
      ;;
    ite_db_port=*)
      ite_db_port="${arg#*=}"
      ;;
    ite_db_name=*)
      ite_db_name="${arg#*=}"
      ;;
    *)
      echo "Unknown argument: $arg"
      ;;
  esac
done

# Check if all required arguments are provided
if [ -z "$vpn_user" ] || [ -z "$vpn_password" ] || [ -z "$vpn_ip_address" ] || [ -z "$vpn_psk" ] || \
   [ -z "$db_username" ] || [ -z "$db_password" ] || [ -z "$db_hostname" ] || [ -z "$db_port" ] || \
   [ -z "$db_name" ] || [ -z "$minio_host" ] || [ -z "$minio_port" ] || [ -z "$oci_key_content" ] || \
   [ -z "$oci_user" ] || [ -z "$oci_fingerprint" ] || [ -z "$oci_tenancy" ] || [ -z "$ite_vpn_url" ] || [ -z "$ite_vpn_user" ] || [ -z "$ite_vpn_password" ]; then
  echo "Error: Missing required arguments."
  echo "Usage: $0 vpn_user=value vpn_password=value vpn_ip_address=value vpn_psk=value \
db_username=value db_password=value db_hostname=value db_port=value db_name=value \
minio_host=value minio_port=value oci_key_content=value oci_user=value oci_fingerprint=value oci_tenancy=value"
  exit 1
fi

vpn_user=""
vpn_password=""
vpn_ip_address=""
vpn_psk=""
db_username=""
db_password=""
db_hostname=""
db_port=""
db_name=""
minio_host=""
minio_port=""
oci_key_content=""
oci_user=""
oci_fingerprint=""
oci_tenancy=""
ite_vpn_url=""
ite_vpn_user=""
ite_vpn_password=""

echo $datetime

mkdir $dicom_directory

echo "Removing old containers..."

docker rm -f myvpncontainer
docker rm -f ai-db
docker rm -f storescp-container
docker rm -f pg-tunnel-c

echo "Running new containers..."

docker run -v $dicom_directory:/data --name storescp-container --network host storescp-image &

make -C $makefile run vpn_user=$vpn_user vpn_password=$vpn_password vpn_ip_address=$vpn_ip_address vpn_psk=$vpn_psk

docker build -t ai-db-writer .
# docker run --name ai-db --privileged --cap-add NET_ADMIN -v $dicom_directory:/iors \
    # -e DB_USERNAME="$db_username" \
    # -e DB_PASSWORD="$db_password" \
    # -e DB_HOSTNAME="$db_hostname" \
    # -e DB_PORT="$db_port" \
    # -e DB_NAME="$db_name" \
    # -e MINIO_HOST="$minio_host" \
    # -e MINIO_PORT="$minio_port" \
    # -e OCI_KEY_CONTENT="$oci_key_content" \
    # -e OCI_USER="$oci_user" \
    # -e OCI_FINGERPRINT="$oci_fingerprint" \
    # -e OCI_TENANCY="$oci_tenancy" \
    # -e ITE_VPN_URL="$ite_vpn_url" \
    # -e ITE_VPN_USER="$ite_vpn_user" \
    # -e ITE_VPN_PASSWORD="$ite_vpn_password" \
    # -e ITE_DB_USERNAME="$ite_db_username" \
    # -e ITE_DB_PASSWORD="$ite_db_password" \
    # -e ITE_DB_HOSTNAME="$ite_db_hostname" \
    # -e ITE_DB_PORT="$ite_db_port" \
    # -e ITE_DB_NAME="$ite_db_name" \
    # -d ai-db-writer

docker run --name ai-db --privileged --cap-add NET_ADMIN -v $dicom_directory:/iors -e DB_USERNAME="$db_username" -e DB_PASSWORD="$db_password" -e DB_HOSTNAME="$db_hostname" -e DB_PORT="$db_port" -e DB_NAME="$db_name" -e MINIO_HOST="$minio_host" -e MINIO_PORT="$minio_port" -e OCI_KEY_CONTENT="$oci_key_content" -e OCI_USER="$oci_user" -e OCI_FINGERPRINT="$oci_fingerprint" -e OCI_TENANCY="$oci_tenancy" -e ITE_VPN_URL="$ite_vpn_url" -e ITE_VPN_USER="$ite_vpn_user" -e ITE_VPN_PASSWORD="$ite_vpn_password" -e ITE_DB_USERNAME="$ite_db_username" -e ITE_DB_PASSWORD="$ite_db_password" -e ITE_DB_HOSTNAME="$ite_db_hostname" -e ITE_DB_PORT="$ite_db_port" -e ITE_DB_NAME="$ite_db_name" -d ai-db-writer

# docker run --name pg-tunnel-c -p 5434:5434 --privileged --cap-add NET_ADMIN \
    # -e ITE_VPN_URL="$ite_vpn_url" \
    # -e ITE_VPN_USER="$ite_vpn_user" \
    # -e ITE_VPN_PASSWORD="$ite_vpn_password" \
    # -e ITE_DB_HOSTNAME="$ite_db_hostname" \
    # -e ITE_DB_PORT="$ite_db_port" \
    # pg-tunnel-i &

docker run --name pg-tunnel-c -p 5434:5434 --privileged --cap-add NET_ADMIN -e ITE_VPN_URL="$ite_vpn_url" -e ITE_VPN_USER="$ite_vpn_user" -e ITE_VPN_PASSWORD="$ite_vpn_password" -e ITE_DB_HOSTNAME="$ite_db_hostname" -e ITE_DB_PORT="$ite_db_port" pg-tunnel-i &

echo "Connecting containers to docker network..."

docker network connect mamo_network myvpncontainer
docker network connect mamo_network ai-db
docker network connect mamo_network pg-tunnel-c

echo "Downloading images. Started at: $(date '+%Y-%m-%d-%H-%M-%S')"

docker exec myvpncontainer python3 /home/cron_new_dicom.py

echo "Checking for outliers. Started at: $(date '+%Y-%m-%d-%H-%M-%S')"

/home/jovisic/mamo-pacs-cli/outlier-docker/venv/bin/python /home/jovisic/mamo-pacs-cli/outlier-docker/clear_outliers.py $dicom_directory

echo "Doing AI and writing to DB. Started at: $(date '+%Y-%m-%d-%H-%M-%S')"

docker exec ai-db sh -c "cd /L-CAM/L_CAM_VGG16/ && python main.py" && rm -r $dicom_directory

echo "Removing containers..."

docker rm -f myvpncontainer
docker rm -f ai-db
docker rm -f storescp-container
docker rm -f pg-tunnel-c

echo "Ended at: $(date '+%Y-%m-%d-%H-%M-%S')"
