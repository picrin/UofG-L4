set -e
mkdir -p CEL_files
rclone copy gdrive:MD/CEL_files CEL_files/
rclone copy backups gdrive:backups
