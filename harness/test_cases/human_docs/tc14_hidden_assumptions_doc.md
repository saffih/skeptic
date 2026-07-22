# Operations Runbook: Production Deployment

## Overview

This runbook covers the standard deployment procedure for the analytics service to production. Follow each step in order.

## Steps

### Step 1: Pull the Latest Release

```bash
cd /opt/analytics-service
git fetch origin
git checkout tags/v3.2.1
```

### Step 2: Run the Migration

```bash
./scripts/migrate.sh
```

### Step 3: Build the Application

```bash
make build
```

### Step 4: Stop the Current Service

```bash
systemctl stop analytics-service
```

### Step 5: Deploy the New Binary

```bash
sudo cp build/analytics-service /usr/local/bin/analytics-service
sudo chown app:app /usr/local/bin/analytics-service
```

### Step 6: Start the Service

```bash
systemctl restart app
```

### Step 7: Verify Deployment

Confirm the service is healthy:

```bash
curl -f http://localhost:8080/health
```

Expected response: `{"status": "healthy", "version": "3.2.1"}`

Check the logs for startup errors:

```bash
journalctl -u analytics-service --since "5 minutes ago" --no-pager
```
