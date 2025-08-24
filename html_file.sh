export TZ=Asia/Kolkata

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

LOGFILE="outputs/devices_output_${TIMESTAMP}.log"
HTMLFILE="outputs/devices_output_${TIMESTAMP}.html"

ansible-playbook -i inventory.ini show_command.yml  | tee "$LOGFILE"

{
  echo "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Ansible Output - ${TIMESTAMP}</title></head><body><pre style='font-family: monospace; background-color:#f9f9f9; padding:1em;'>"
  cat "$LOGFILE" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'
  echo "</pre></body></html>"
} > "$HTMLFILE"

chmod 444 "$HTMLFILE"

#chmod 444 "$LOGFILE"

rm -f "$LOGFILE"
