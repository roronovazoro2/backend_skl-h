import uuid
from typing import Dict, Any

from app.core.db import supabase_client


class SyncService:
    @staticmethod
    def _normalize_uuid(value: Any) -> str:
        if value is None:
            return str(uuid.uuid4())

        if isinstance(value, uuid.UUID):
            return str(value)

        text = str(value).strip()
        if not text:
            return str(uuid.uuid4())

        try:
            return str(uuid.UUID(text))
        except ValueError:
            return str(uuid.uuid5(uuid.NAMESPACE_URL, text))

    @staticmethod
    def _normalize_payload(entity_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(payload)

        if 'id' in normalized:
            normalized['id'] = SyncService._normalize_uuid(normalized['id'])

        if entity_type == 'crops' and 'farmer_id' in normalized and normalized.get('farmer_id'):
            normalized['farmer_id'] = SyncService._normalize_uuid(normalized['farmer_id'])

        if entity_type == 'jobs' and 'worker_id' in normalized and normalized.get('worker_id'):
            normalized['worker_id'] = SyncService._normalize_uuid(normalized['worker_id'])

        if entity_type in ('workers', 'jobs') and 'farmer_id' in normalized and normalized.get('farmer_id'):
            normalized['farmer_id'] = SyncService._normalize_uuid(normalized['farmer_id'])

        return normalized

    @staticmethod
    def process_queue(items: list[dict]) -> Dict[str, Any]:
        client = supabase_client.get_client()
        processed = 0

        for item in items:
            entity_type = item.get('entity_type')
            payload = SyncService._normalize_payload(entity_type, item.get('payload', {}))
            action = item.get('action', 'CREATE').upper()

            if entity_type not in ('crops', 'workers', 'jobs'):
                continue

            if action == 'DELETE':
                record_id = SyncService._normalize_uuid(payload.get('id') or item.get('entity_id'))
                if record_id:
                    client.table(entity_type).delete().eq('id', record_id).execute()
                    processed += 1
                continue

            if action in ('CREATE', 'UPDATE'):
                record_id = SyncService._normalize_uuid(payload.get('id') or item.get('entity_id'))
                if action == 'UPDATE' and record_id:
                    client.table(entity_type).update(payload).eq('id', record_id).execute()
                else:
                    if 'id' not in payload:
                        payload['id'] = record_id
                    client.table(entity_type).insert(payload).execute()
                processed += 1

        return {"processed": processed, "status": "ok"}

    @staticmethod
    def summarize_sync(payload: Dict[str, Any]) -> Dict[str, Any]:
        result = SyncService.process_queue(payload.get('items', []))
        return {
            "received": True,
            "records": len(payload.get('items', [])),
            "status": result.get('status', 'ok'),
            "processed": result.get('processed', 0),
            "message": "Sync payload processed by Supabase backend."
        }
