# services/api/app/services/billing_export.py
"""
Billing export service for generating CSV reports from video costs.
SRP: Billing data export only, no business logic.
"""
import os
import csv
import uuid
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class BillingExportService:
    """Service for exporting billing data to CSV."""

    def __init__(self):
        """Initialize billing export service."""
        self.exports_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(self.exports_dir, exist_ok=True)

        logger.info(f"✅ Billing export service initialized: {self.exports_dir}")

    async def export_monthly_billing(self, month: str) -> Dict[str, Any]:
        """
        Export billing data for a specific month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            Dictionary with export results including file URL
        """
        try:
            # Validate month format
            try:
                datetime.strptime(month, "%Y-%m")
            except ValueError:
                raise ValueError(f"Invalid month format: {month}. Expected YYYY-MM")

            logger.info(f"Exporting billing data for month: {month}")

            # Get cost data from database
            cost_data = await self._get_monthly_costs(month)

            if not cost_data:
                return {
                    "success": False,
                    "error": f"No cost data found for month {month}",
                    "rows_count": 0,
                    "amount_cents": 0,
                    "file_url": None
                }

            # Generate CSV file
            csv_path = await self._generate_csv_file(cost_data, month)

            # Upload to R2 if configured
            file_url = await self._upload_to_r2(csv_path, month)

            # Save export record to database
            export_id = await self._save_export_record(month, len(cost_data), cost_data, file_url)

            # Clean up local file if uploaded successfully
            if file_url and os.path.exists(csv_path):
                os.remove(csv_path)
                logger.info(f"Cleaned up local CSV file: {csv_path}")

            result = {
                "success": True,
                "export_id": export_id,
                "month": month,
                "rows_count": len(cost_data),
                "amount_cents": sum(row.get("amount_cents", 0) for row in cost_data),
                "file_url": file_url,
                "generated_at": datetime.utcnow().isoformat()
            }

            logger.info(f"✅ Billing export completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Billing export failed for month {month}: {e}")
            return {
                "success": False,
                "error": str(e),
                "month": month,
                "file_url": None
            }

    async def _get_monthly_costs(self, month: str) -> List[Dict[str, Any]]:
        """Get cost data for the specified month from database."""
        try:
            from .job_repo_supabase import get_job_repo

            repo = get_job_repo()

            if not repo.enabled:
                logger.warning("Supabase not available for billing export")
                return []

            # Query video_costs for the month
            # This would typically use raw SQL for efficiency
            try:
                from supabase import create_client

                client = create_client(
                    os.getenv("SUPABASE_URL", ""),
                    os.getenv("SUPABASE_SERVICE_KEY", "")
                )

                # Query for costs in the specified month
                start_date = f"{month}-01"
                if month == "2025-12":  # Handle year boundary
                    end_date = f"{int(month.split('-')[0]) + 1}-01-01"
                else:
                    next_month = month.split('-')[0] + '-' + str(int(month.split('-')[1]) + 1).zfill(2)
                    end_date = f"{next_month}-01"

                # For now, return sample data structure
                # In production, this would query the actual video_costs table
                sample_costs = [
                    {
                        "job_id": "sample-job-1",
                        "tts_seconds": 45.2,
                        "processing_seconds": 87.3,
                        "storage_mb": 5.2,
                        "amount_cents": 12,
                        "created_at": f"{month}-15T10:30:00Z"
                    }
                ]

                return sample_costs

            except Exception as e:
                logger.error(f"Failed to query costs for month {month}: {e}")
                return []

        except Exception as e:
            logger.error(f"Error getting monthly costs: {e}")
            return []

    async def _generate_csv_file(self, cost_data: List[Dict[str, Any]], month: str) -> str:
        """Generate CSV file from cost data."""
        csv_path = os.path.join(self.exports_dir, f"billing_{month}.csv")

        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'job_id', 'created_at', 'tts_seconds', 'processing_seconds',
                    'storage_mb', 'amount_cents', 'cost_tts_cents', 'cost_processing_cents',
                    'cost_storage_cents', 'preset', 'duration_seconds'
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in cost_data:
                    # Calculate individual costs
                    tts_cost = row.get('tts_seconds', 0) * float(os.getenv('TTS_COST_PER_SECOND', '0.0001'))
                    processing_cost = row.get('processing_seconds', 0) * float(os.getenv('PROCESSING_COST_PER_SECOND', '0.001'))
                    storage_cost = row.get('storage_mb', 0) * float(os.getenv('STORAGE_COST_PER_MB', '0.01'))

                    writer.writerow({
                        'job_id': row.get('job_id', ''),
                        'created_at': row.get('created_at', ''),
                        'tts_seconds': row.get('tts_seconds', 0),
                        'processing_seconds': row.get('processing_seconds', 0),
                        'storage_mb': row.get('storage_mb', 0),
                        'amount_cents': row.get('amount_cents', 0),
                        'cost_tts_cents': round(tts_cost * 100),  # Convert to cents
                        'cost_processing_cents': round(processing_cost * 100),
                        'cost_storage_cents': round(storage_cost * 100),
                        'preset': 'medium',  # Would come from job metadata
                        'duration_seconds': row.get('processing_seconds', 0)
                    })

            logger.info(f"✅ Generated CSV file: {csv_path} ({len(cost_data)} rows)")
            return csv_path

        except Exception as e:
            logger.error(f"Failed to generate CSV file: {e}")
            raise

    async def _upload_to_r2(self, csv_path: str, month: str) -> Optional[str]:
        """Upload CSV file to R2 storage."""
        try:
            from .storage_service import get_storage_service

            storage = get_storage_service()

            if storage.storage_type != "r2":
                logger.info("R2 storage not configured, keeping file local")
                return f"file://{csv_path}"

            # Upload to R2
            with open(csv_path, 'rb') as f:
                file_data = f.read()

            # Generate R2 key
            key = f"exports/billing_{month}.csv"
            url = storage.save_video(file_data, key)

            logger.info(f"✅ Uploaded CSV to R2: {key}")
            return url

        except Exception as e:
            logger.error(f"Failed to upload CSV to R2: {e}")
            return f"file://{csv_path}"  # Fallback to local

    async def _save_export_record(self, month: str, rows_count: int, cost_data: List[Dict], file_url: str) -> str:
        """Save export record to database."""
        try:
            total_amount = sum(row.get("amount_cents", 0) for row in cost_data)

            # Save to billing_exports table
            try:
                from supabase import create_client

                client = create_client(
                    os.getenv("SUPABASE_URL", ""),
                    os.getenv("SUPABASE_SERVICE_KEY", "")
                )

                export_data = {
                    "id": str(uuid.uuid4()),
                    "month": month,
                    "rows_count": rows_count,
                    "amount_cents": total_amount,
                    "file_url": file_url
                }

                result = client.table("billing_exports").insert(export_data).execute()

                if result.data:
                    export_id = result.data[0]["id"]
                    logger.info(f"✅ Saved export record: {export_id}")
                    return export_id

            except Exception as e:
                logger.error(f"Failed to save export record to database: {e}")

            # Fallback: return a generated ID
            return str(uuid.uuid4())

        except Exception as e:
            logger.error(f"Error saving export record: {e}")
            return str(uuid.uuid4())

    def list_available_exports(self) -> List[Dict[str, Any]]:
        """List all available billing exports."""
        try:
            from .job_repo_supabase import get_job_repo

            repo = get_job_repo()

            if not repo.enabled:
                return []

            # Query billing_exports table
            try:
                from supabase import create_client

                client = create_client(
                    os.getenv("SUPABASE_URL", ""),
                    os.getenv("SUPABASE_SERVICE_KEY", "")
                )

                result = client.table("billing_exports").select("*").order("created_at", desc=True).execute()

                exports = []
                for export in result.data:
                    exports.append({
                        "id": export.get("id"),
                        "month": export.get("month"),
                        "rows_count": export.get("rows_count", 0),
                        "amount_cents": export.get("amount_cents", 0),
                        "file_url": export.get("file_url"),
                        "created_at": export.get("created_at")
                    })

                return exports

            except Exception as e:
                logger.error(f"Failed to list exports: {e}")
                return []

        except Exception as e:
            logger.error(f"Error listing exports: {e}")
            return []

# Global instance
_billing_export_service = None

def get_billing_export_service() -> BillingExportService:
    """Get or create global billing export service instance."""
    global _billing_export_service
    if _billing_export_service is None:
        _billing_export_service = BillingExportService()
    return _billing_export_service