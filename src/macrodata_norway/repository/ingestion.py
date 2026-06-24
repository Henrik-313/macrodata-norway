from sqlalchemy import text

from macrodata_norway.db.engine import get_engine


def start_ingestion_run(
    source_id: int | None,
    run_type: str,
) -> int:
    """
    Start new ingestion run.

    This creates a row with status=running and returns the run id.
    """

    engine = get_engine()

    sql = """
    INSERT INTO ingestion_run (
        source_id,
        run_type,
        status
    )
    VALUES (
        :source_id,
        :run_type,
        'running'
    )
    RETURNING id;
    """

    query = text(sql)

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "source_id": source_id,
                "run_type": run_type,
            },
        )

        run_id = result.scalar_one()

        return run_id


def finish_ingestion_run(
    run_id: int,
    status: int,
    rows_fetched: int = 0,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    rows_skipped: int = 0,
    error_message: str | None = None,
) -> None:
    """
    Mark an ingestion run as finished.

    status should usually be
        succsess
        partial
        failed
    """

    engine = get_engine()

    sql = """ 

    UPDATE ingestion_run
    SET 
        status = :status,
        finished_at = now(),
        rows_fetched = :rows_fetched,
        rows_inserted = :rows_inserted,
        rows_updated = :rows_updated,
        rows_skipped =  :rows_skipped,
        error_message = :error_message
    WHERE id = :run_id;
    
    """

    query = text(sql)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "run_id": run_id,
                "status": status,
                "rows_fetched": rows_fetched,
                "rows_inserted": rows_inserted,
                "rows_updated": rows_updated,
                "rows_skipped": rows_skipped,
                "error_message": error_message,
            },
        )


def failed_ingestion_run(
    run_id: int,
    error_message: str,
    rows_fetched: int = 0,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    rows_skipped: int = 0,
) -> None:
    """
    Convenivence function for marking a run as failed.
    """

    finish_ingestion_run(
        run_id=run_id,
        status="failed",
        rows_fetched=rows_fetched,
        rows_inserted=rows_inserted,
        rows_updated=rows_updated,
        rows_skipped=rows_skipped,
        error_message=error_message,
    )
