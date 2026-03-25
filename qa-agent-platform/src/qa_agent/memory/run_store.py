import sqlite3
from typing import Dict, Any
from qa_agent.graph.state import GraphState
import json

class SQLiteRunStore:
    def __init__(self, db_path: str = "data/runs/runs.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                mission_id TEXT PRIMARY KEY,
                user_input TEXT,
                state_json TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # We can add more tables later based on requirements for:
        # tasks, tool_calls, artifacts, work_items, checkpoints
        
        conn.commit()
        conn.close()
        
    def save_run(self, state: GraphState, status: str = "running"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        state_dump = state.model_dump_json()
        
        cursor.execute('''
            INSERT INTO runs (mission_id, user_input, state_json, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(mission_id) DO UPDATE SET
                state_json=excluded.state_json,
                status=excluded.status
        ''', (state.mission.mission_id, state.mission.user_input, state_dump, status))
        
        conn.commit()
        conn.close()

    def get_run(self, mission_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT state_json, status FROM runs WHERE mission_id = ?', (mission_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "state": json.loads(row[0]),
                "status": row[1]
            }
        return None
