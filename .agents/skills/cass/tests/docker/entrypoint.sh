#!/bin/bash
# Entrypoint script for SSH test container
# Allows injecting authorized keys via environment variable or volume mount

set -e

# If SSH_AUTHORIZED_KEY is provided, add it
if [ -n "$SSH_AUTHORIZED_KEY" ]; then
    echo "$SSH_AUTHORIZED_KEY" > /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    echo "Added authorized key from environment"
fi

# If authorized_keys file was mounted, ensure correct permissions
if [ -f /root/.ssh/authorized_keys ]; then
    chmod 600 /root/.ssh/authorized_keys
    chown root:root /root/.ssh/authorized_keys
fi

# Print SSH fingerprints for debugging
echo "SSH host key fingerprints:"
for key in /etc/ssh/ssh_host_*_key.pub; do
    ssh-keygen -lf "$key" 2>/dev/null || true
done

# Start SSH daemon
exec "$@"
