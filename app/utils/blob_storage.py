"""
Azure Blob Storage helper.
Persists the final review report as JSON so it can be shared / retrieved later.
"""

import json
import os
from datetime import datetime, timezone

from azure.storage.blob import BlobServiceClient, ContentSettings


CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
CONTAINER_NAME    = os.getenv("BLOB_CONTAINER_NAME", "reports")


def _get_client() -> BlobServiceClient:
    if not CONNECTION_STRING:
        raise EnvironmentError(
            "AZURE_STORAGE_CONNECTION_STRING is not set in your .env file."
        )
    return BlobServiceClient.from_connection_string(CONNECTION_STRING)


def upload_report(review_id: str, report: dict) -> str:
    """
    Upload a review report dict as JSON to Azure Blob Storage.
    Returns the blob URL (public read URL if container is set to allow it).
    """
    client = _get_client()
    container_client = client.get_container_client(CONTAINER_NAME)

    blob_name = f"{datetime.now(timezone.utc).strftime('%Y/%m/%d')}/{review_id}.json"
    blob_client = container_client.get_blob_client(blob_name)

    blob_client.upload_blob(
        data=json.dumps(report, indent=2, default=str),
        overwrite=True,
        content_settings=ContentSettings(content_type="application/json"),
    )

    return blob_client.url


def download_report(review_id: str) -> dict | None:
    """Download a previously stored report by its review_id. Returns None if not found."""
    client = _get_client()
    container_client = client.get_container_client(CONTAINER_NAME)

    # Search by prefix (we don't know the exact date path)
    blobs = list(container_client.list_blobs(name_starts_with=""))
    target = next((b for b in blobs if review_id in b.name), None)
    if not target:
        return None

    blob_client = container_client.get_blob_client(target.name)
    data = blob_client.download_blob().readall()
    return json.loads(data)
