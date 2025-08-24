#!/bin/bash

# Load environment for cron compatibility
export TZ=Asia/Kolkata
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Activate virtual environment
source /home/nipun/my_ansible_project/ansible-env/bin/activate

# Generate timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_DIR="/home/nipun/my_ansible_project/backups/${TIMESTAMP}"

# Inventory groups
INVENTORIES=("acc" "dis" "core")

# Run playbook per inventory
for INV in "${INVENTORIES[@]}"; do
    INVENTORY_FILE="/home/nipun/my_ansible_project/inventory_${INV}.ini"
    SUB_OUTPUT_DIR="${OUTPUT_DIR}/${INV}"
    mkdir -p "$SUB_OUTPUT_DIR"

    ansible-playbook \
        -i "$INVENTORY_FILE" /home/nipun/my_ansible_project/show_command_2.yml \
        -e "timestamp=$TIMESTAMP output_dir=$SUB_OUTPUT_DIR"
done

# Cleanup backups older than 7 days
find /home/nipun/my_ansible_project/backups/ -mindepth 1 -maxdepth 1 -type d -mtime +7 -exec rm -r {} \;
