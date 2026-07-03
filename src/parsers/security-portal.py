import pandas as pd
from src.db import upsert_metric_by_date, recalculate_pulse_scores

def parse_esentire_csv(file_buffer):
    """
    Parses an Security-Portal Atlas CSV export.
    Expects columns indicating alert timestamps and severity.
    """
    try:
        df = pd.read_csv(file_buffer)
        
        date_col = next((col for col in df.columns if 'date' in col.lower() or 'time' in col.lower() or 'created' in col.lower()), None)
        
        if not date_col:
            raise ValueError(f"Could not identify date column. Found: {df.columns.tolist()}")

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        # Count total incidents per day
        daily_counts = df.groupby(df[date_col].dt.date).size().reset_index(name='incident_count')
        
        records_processed = 0
        for index, row in daily_counts.iterrows():
            upsert_metric_by_date(row[date_col], 'esentire_active_incidents', int(row['incident_count']))
            records_processed += 1
            
        recalculate_pulse_scores()
        return True, f"Successfully parsed {records_processed} daily incident totals into the timeline."
        
    except Exception as e:
        return False, f"Failed to parse Security-Portal CSV: {str(e)}"
