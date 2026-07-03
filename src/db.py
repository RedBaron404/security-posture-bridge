import sqlite3
import pandas as pd
from contextlib import contextmanager

DB_FILE = 'db/sentinel.db'

@contextmanager
def get_db_connection():
    """Provides a managed database connection."""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initializes the SQLite schema."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Table for storing historical pulse scores and high-level vendor metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_metrics (
                date_string TEXT PRIMARY KEY,
                timestamp DATETIME,
                pulse_score REAL DEFAULT 0,
                knowbe4_ppp REAL DEFAULT 0,
                esentire_active_incidents INTEGER DEFAULT 0,
                google_alerts_24h INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_date DATE,
                incident_type TEXT,
                root_cause TEXT,
                remediation TEXT,
                logged_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

def upsert_metric_by_date(date_obj, vendor_col, value):
    """
    Inserts or updates a specific vendor metric for a given date.
    vendor_col must be one of: 'knowbe4_ppp', 'esentire_active_incidents', 'google_alerts_24h'
    """
    date_str = date_obj.strftime("%Y-%m-%d")
    timestamp_val = pd.to_datetime(date_str)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Insert if doesn't exist, else update the specific metric
        query = f'''
            INSERT INTO historical_metrics (date_string, timestamp, {vendor_col})
            VALUES (?, ?, ?)
            ON CONFLICT(date_string) DO UPDATE SET
            {vendor_col} = excluded.{vendor_col}
        '''
        cursor.execute(query, (date_str, timestamp_val, value))
        conn.commit()
        
def recalculate_pulse_scores():
    """Iterates through historical_metrics and calculates the unified pulse score, applying forward-fill for blank vendor data."""
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM historical_metrics ORDER BY date_string ASC", conn)
        
        if not df.empty:
            # Forward fill 0s with previous actual values to create a contiguous trend if some CSVs skip days
            df[['knowbe4_ppp', 'esentire_active_incidents', 'google_alerts_24h']] = df[['knowbe4_ppp', 'esentire_active_incidents', 'google_alerts_24h']].replace(0, pd.NA).ffill().fillna(0)
            
            for index, row in df.iterrows():
                human_score = min(row['knowbe4_ppp'] * 2, 100)
                mdr_score = min(row['esentire_active_incidents'] * 10, 100)
                admin_score = min(row['google_alerts_24h'] * 2, 100)
                
                pulse = (human_score * 0.35) + (mdr_score * 0.40) + (admin_score * 0.25)
                
                cursor = conn.cursor()
                cursor.execute('UPDATE historical_metrics SET pulse_score = ? WHERE date_string = ?', (pulse, row['date_string']))
            conn.commit()
        
def get_historical_trends(days=None) -> pd.DataFrame:
    """Returns the historical metric snapshots. If days is passed, filters by range."""
    with get_db_connection() as conn:
        query = "SELECT * FROM historical_metrics ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if days is not None:
                cutoff_date = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
                # Ensure tz-awareness compatibility
                if df['timestamp'].dt.tz is None:
                    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
                df = df[df['timestamp'] >= cutoff_date]
                
        return df

def clear_historical_metrics():
    """Wipes the metrics table. Re-ingesting a CSV will rewrite history."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM historical_metrics")
        conn.commit()

def add_incident(date, type, cause, remediation):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO incidents (incident_date, incident_type, root_cause, remediation)
            VALUES (?, ?, ?, ?)
        ''', (date, type, cause, remediation))
        conn.commit()

def get_recent_incidents(limit=10) -> pd.DataFrame:
    with get_db_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM incidents ORDER BY incident_date DESC LIMIT {limit}", conn)
        return df

# Initialize the schema upon first import of this module
init_db()
