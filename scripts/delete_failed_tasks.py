#!/usr/bin/env python3
"""
Supprime toutes les tâches échouées de analysis_tasks.
Utilise l'API REST pour chaque tâche.
"""

import requests
import sys

API_BASE = "http://localhost:8080/api/analysis"

def get_all_failed_tasks():
    """Récupère toutes les tâches failed (pas de limite)"""
    url = f"{API_BASE}/failed-tasks?limit=100"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        print(f"Erreur récupération failed tasks: {resp.status_code}")
        return []
    return resp.json()

def delete_task(task_id):
    """Supprime une tâche par son ID"""
    url = f"{API_BASE}/tasks/{task_id}"
    resp = requests.delete(url, timeout=10)
    return resp.status_code in (200, 204)

def main():
    tasks = get_all_failed_tasks()
    total = len(tasks)
    print(f"Found {total} failed tasks")
    deleted = 0
    failed = 0
    for task in tasks:
        tid = task.get('id')
        title = task.get('title', '?')
        if not tid:
            continue
        ok = delete_task(tid)
        if ok:
            print(f"[OK] Deleted: {title} ({tid})")
            deleted += 1
        else:
            print(f"[FAIL] Could not delete: {title} ({tid})")
            failed += 1
    print(f"\nSummary: {deleted} deleted, {failed} failures")

if __name__ == "__main__":
    main()
