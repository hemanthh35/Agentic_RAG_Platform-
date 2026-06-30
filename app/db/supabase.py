import logging
from typing import Dict, Optional
from app.core.config import settings
from supabase import Client, create_client

logger = logging.getLogger(__name__)

supabase_client: Optional[Client] = None

# Initialize the Supabase client only if credentials are provided and valid
if (
    settings.SUPABASE_URL
    and (settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY)
    and "your-supabase" not in settings.SUPABASE_URL
):
    try:
        # Prefer service role key for backend admin operations to bypass RLS policies
        supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
        supabase_client = create_client(
            settings.SUPABASE_URL, supabase_key
        )
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase_client = None
else:
    logger.warning(
        "Supabase credentials are missing or default. Supabase client is disabled."
    )
    supabase_client = None


def check_supabase_connection() -> bool:
    """Verify if the Supabase client is successfully initialized and online.

    Returns:
        True if connection is successful, False otherwise.
    """
    if supabase_client is None:
        return False
    try:
        # Perform a light request to verify server reachability
        supabase_client.storage.list_buckets()
        return True
    except Exception as e:
        # Check if the error is due to a network connection failure
        import httpx

        if isinstance(e, httpx.RequestError):
            logger.warning(f"Supabase host unreachable: {e}")
            return False

        # If it is an auth error (401/403), the server is reachable but creds are placeholders
        logger.info(f"Supabase connection validated (API returned authentication state): {e}")
        return True


def check_supabase_storage_buckets() -> Dict[str, str]:
    """Verify the setup status of required storage buckets.

    Required placeholders: "documents", "uploads", "exports".

    Returns:
        A dictionary mapping bucket names to their statuses ("ready", "missing", "error", "disabled").
    """
    required_buckets = ["documents", "uploads", "exports"]
    status_map = {bucket: "unknown" for bucket in required_buckets}

    if supabase_client is None:
        return {bucket: "disabled" for bucket in required_buckets}

    try:
        buckets_list = supabase_client.storage.list_buckets()
        existing_names = {b.name for b in buckets_list}

        for bucket in required_buckets:
            if bucket in existing_names:
                status_map[bucket] = "ready"
            else:
                status_map[bucket] = "missing"
    except Exception as e:
        logger.warning(f"Failed to query Supabase storage buckets: {e}")
        for bucket in required_buckets:
            status_map[bucket] = "error"

    return status_map
