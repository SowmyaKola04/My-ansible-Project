export TZ=Asia/Kolkata

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%s")

LOGFILE="outputs/devices_output_${TIMESTAMP}.log"

ansible-playbook -i inventory.ini show_command.yml  | tee "$LOGFILE"

chmod 444 "$LOGFILE"

echo "File $LOGFILE is now read-only and immutable."
