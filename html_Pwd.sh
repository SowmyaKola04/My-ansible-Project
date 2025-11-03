export TZ=Asia/Kolkata

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
HTMLFILE="outputs/devices_output_${TIMESTAMP}.html"
PASSPHRASE="XXXX"


TEMPFILE=$(mktemp)
ansible-playbook -i inventory.ini show_command.yml | sed -r "s/\x1B\[[0-9;]*[mGKH]//g" > "$TEMPFILE"

{
echo "<!DOCTYPE html>"
echo "<html><head><meta charset='UTF-8'><title>Secure Report - ${TIMESTAMP}</title>"
echo "<script>"
echo "function decrypt() {"
echo "  const pass = prompt('Enter access key:');"
echo "  if (pass === '${PASSPHRASE}') {"
echo "    document.getElementById('secure').style.display = 'block';"
echo "    document.getElementById('auth').style.display = 'none';"
echo "  } else {"
echo "    alert('Incorrect key. Access denied.');"
echo "  }"
echo "}"
echo "window.onload = decrypt;"
echo "</script>"
echo "</head><body>"
echo "<div id='auth'><p style='color:red;'>🔐 This file is Protected. Enter the key to access the file.</p></div>"
echo "<div id='secure' style='display:none;'><pre style='font-family:monospace; background:#f9f9f9; padding:1em;'>"

sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g' "$TEMPFILE"

echo "</pre></div></body></html>"
} > "$HTMLFILE"

chmod 444 "$HTMLFILE"

rm -f "$TEMPFILE"

