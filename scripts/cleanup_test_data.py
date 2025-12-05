#!/usr/bin/env python3
"""
Cleanup script to remove all test/placeholder data from production Cosmos DB.
Uses the API endpoints to delete items.
"""
import requests
import sys

API_URL = "https://agent-arch-api-prod.azurewebsites.net"
API_KEY = "od6Ty_uDZovVXQeF_LfrAbSkuhoJvkBg0axdHftoE10"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_items(endpoint):
    """Get all items from an endpoint."""
    resp = requests.get(f"{API_URL}/api/{endpoint}", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data if isinstance(data, list) else data.get('items', [])
    return []

def delete_item(endpoint, item_id):
    """Delete a single item."""
    resp = requests.delete(f"{API_URL}/api/{endpoint}/{item_id}", headers=headers)
    return resp.status_code in [200, 204, 404]

def clear_container(name, endpoint=None):
    """Clear all items from a container."""
    endpoint = endpoint or name
    items = get_items(endpoint)
    count = len(items)

    if count == 0:
        print(f"  {name}: already empty")
        return 0

    deleted = 0
    for item in items:
        item_id = item.get('id')
        if item_id and delete_item(endpoint, item_id):
            deleted += 1
            print(f"  {name}: deleted {item_id}")
        else:
            print(f"  {name}: failed to delete {item_id}")

    print(f"  {name}: deleted {deleted}/{count} items")
    return deleted

def clear_audit_logs():
    """Clear audit logs - may need special handling."""
    resp = requests.get(f"{API_URL}/api/audit?limit=1000", headers=headers)
    if resp.status_code != 200:
        print("  audit_logs: could not fetch")
        return 0

    data = resp.json()
    items = data.get('items', [])
    count = len(items)

    if count == 0:
        print("  audit_logs: already empty")
        return 0

    deleted = 0
    for item in items:
        item_id = item.get('id')
        if item_id:
            resp = requests.delete(f"{API_URL}/api/audit/{item_id}", headers=headers)
            if resp.status_code in [200, 204, 404]:
                deleted += 1

    print(f"  audit_logs: deleted {deleted}/{count} items")
    return deleted

def clear_snapshots():
    """Clear snapshots using the dedicated endpoint."""
    resp = requests.delete(f"{API_URL}/api/snapshots", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"  snapshots: cleared {data.get('deleted_count', 0)} items")
        return data.get('deleted_count', 0)
    print(f"  snapshots: clear failed (status {resp.status_code})")
    return 0

def main():
    print("=" * 50)
    print("Production Data Cleanup")
    print("=" * 50)
    print(f"Target: {API_URL}")
    print()

    # Confirm
    if len(sys.argv) < 2 or sys.argv[1] != "--confirm":
        print("This will DELETE ALL DATA from the production database!")
        print("Run with --confirm to proceed")
        return

    print("Starting cleanup...")
    print()

    total = 0

    # Clear main containers
    total += clear_container("meetings")
    total += clear_container("tasks")
    total += clear_container("agents")
    total += clear_container("proposals")
    total += clear_container("decisions")

    # Clear audit logs
    total += clear_audit_logs()

    # Clear snapshots
    total += clear_snapshots()

    print()
    print("=" * 50)
    print(f"Cleanup complete. Total items deleted: {total}")
    print("=" * 50)

if __name__ == "__main__":
    main()
