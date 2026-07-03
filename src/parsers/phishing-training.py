import pandas as pd
from src.db import upsert_metric_by_date, recalculate_pulse_scores

def parse_knowbe4_csv(file_buffer):
    """
    Parses a KnownBe4 Phishing Campaign Export.
    Expects event-level columns like: 'Delivered (UTC)', 'Clicked (UTC)', 'Replied (UTC)', etc.
    Calculates the Phish-Prone Percentage (PPP) per day.
    """
    try:
        df = pd.read_csv(file_buffer)
        
        # Check for expected delivery column
        if 'Delivered (UTC)' not in df.columns:
            # Fallback heuristic if exact name differs
            date_col = next((col for col in df.columns if 'deliver' in col.lower() or 'date' in col.lower()), None)
        else:
            date_col = 'Delivered (UTC)'

        if not date_col:
            raise ValueError(f"Could not identify a Delivery Date column. Found: {df.columns.tolist()}")
            
        # Parse delivery dates robustly and drop rows without a delivery date
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        # Define what constitutes a "failure" in a phishing campaign
        failure_cols = [col for col in df.columns if any(x in col.lower() for x in ['click', 'repl', 'attach', 'data'])]
        
        if not failure_cols:
            raise ValueError(f"Could not identify failure columns (Clicks, Replies, etc.) to calculate PPP. Found: {df.columns.tolist()}")
            
        # A row is a failure if ANY of the failure columns are NOT null/empty
        df['is_failure'] = df[failure_cols].notna().any(axis=1)
        
        # Group by day to calculate daily PPP
        df['date_only'] = df[date_col].dt.date
        daily_stats = df.groupby('date_only').agg(
            total_delivered=('is_failure', 'count'),
            total_failures=('is_failure', 'sum')
        ).reset_index()
        
        # Calculate PPP: (failures / delivered) * 100
        daily_stats['ppp_percentage'] = (daily_stats['total_failures'] / daily_stats['total_delivered']) * 100
        
        records_processed = 0
        for index, row in daily_stats.iterrows():
            if row['total_delivered'] > 0:
                upsert_metric_by_date(pd.to_datetime(row['date_only']), 'knowbe4_ppp', float(row['ppp_percentage']))
                records_processed += 1
                
        recalculate_pulse_scores()
        return True, f"Successfully parsed {records_processed} campaign days and calculated daily PPP."

    except Exception as e:
        return False, f"Failed to parse Phishing-Training CSV: {str(e)}"
