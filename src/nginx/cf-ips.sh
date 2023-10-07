#!/bin/bash

# Define the URLs for Cloudflare IPs
CF_IPV4_URL="https://www.cloudflare.com/ips-v4"
CF_IPV6_URL="https://www.cloudflare.com/ips-v6"

# Define the output file
OUTPUT_FILE="cf-ips.conf"

# Function to add IPs from a URL to the output file
add_ips_from_url() {
  local url="$1"
  curl -sS "$url" | while read -r ip; do
    echo "allow $ip;" >> "$OUTPUT_FILE"
  done
}

# Clear existing contents of the output file
> "$OUTPUT_FILE"

# Add IPv4 IPs
add_ips_from_url "$CF_IPV4_URL"

# Add IPv6 IPs
add_ips_from_url "$CF_IPV6_URL"

echo "Cloudflare IPs have been saved to $OUTPUT_FILE"
