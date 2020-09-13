set -e

target="$1"
echo "Starting portscan of $target..."
ports=$(nmap -p- --min-rate=1000 -T4 $target | grep ^[0-9] | cut -d '/' -f 1 | tr '\n' ',' | sed s/,$//)
echo "Interesting ports are: $ports"
echo "Starting nmap of $target..."
nmap -sC -sV -p$ports $target
