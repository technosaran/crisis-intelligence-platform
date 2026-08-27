import { openDB } from 'idb';

const DB_NAME = 'crisis_offline_db';
const STORE_NAME = 'request_queue';

async function getDB() {
  return openDB(DB_NAME, 1, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
      }
    },
  });
}

export async function queueRequest(url: string, method: string, body: any) {
  const db = await getDB();
  await db.add(STORE_NAME, {
    url,
    method,
    body,
    timestamp: Date.now(),
  });
  console.log('Request queued for offline sync');
}

export async function syncOfflineQueue() {
  const db = await getDB();
  const tx = db.transaction(STORE_NAME, 'readwrite');
  const store = tx.objectStore(STORE_NAME);
  const requests = await store.getAll();

  if (requests.length === 0) return;
  console.log(`Syncing ${requests.length} offline requests...`);

  for (const req of requests) {
    try {
      const res = await fetch(req.url, {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(req.body),
      });

      if (res.ok) {
        await store.delete(req.id);
      }
    } catch (err) {
      console.error('Failed to sync request, will retry later:', err);
    }
  }
}
