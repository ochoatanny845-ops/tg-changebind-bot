"""
数据库操作
"""
import sqlite3
import time
from config import Config

class Database:
    """数据库管理"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 创建账号表
        c.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                old_phone TEXT NOT NULL,
                new_phone TEXT,
                api_url_old TEXT NOT NULL,
                api_url_new TEXT,
                session_file TEXT NOT NULL,
                login_time INTEGER NOT NULL,
                ready_time INTEGER NOT NULL,
                changebind_time INTEGER,
                status TEXT NOT NULL,
                device_model TEXT,
                error_message TEXT,
                created_at INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_account(self, old_phone, api_url_old, session_file, device_model):
        """添加账号（登录后）"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        login_time = int(time.time())
        ready_time = login_time + 86400  # 24小时后
        
        c.execute('''
            INSERT INTO accounts 
            (old_phone, api_url_old, session_file, login_time, ready_time, status, device_model, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (old_phone, api_url_old, session_file, login_time, ready_time, 'pending', device_model, login_time))
        
        account_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return account_id
    
    def get_account(self, account_id):
        """获取账号信息"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'old_phone': row[1],
            'new_phone': row[2],
            'api_url_old': row[3],
            'api_url_new': row[4],
            'session_file': row[5],
            'login_time': row[6],
            'ready_time': row[7],
            'changebind_time': row[8],
            'status': row[9],
            'device_model': row[10],
            'error_message': row[11],
            'created_at': row[12]
        }
    
    def get_all_accounts(self):
        """获取所有账号"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM accounts ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            accounts.append({
                'id': row[0],
                'old_phone': row[1],
                'new_phone': row[2],
                'api_url_old': row[3],
                'api_url_new': row[4],
                'session_file': row[5],
                'login_time': row[6],
                'ready_time': row[7],
                'changebind_time': row[8],
                'status': row[9],
                'device_model': row[10],
                'error_message': row[11],
                'created_at': row[12]
            })
        
        return accounts
    
    def get_ready_accounts(self):
        """获取就绪的账号（24小时已过）"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = int(time.time())
        c.execute('''
            SELECT * FROM accounts 
            WHERE status = 'pending' AND ready_time <= ?
        ''', (now,))
        
        rows = c.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            accounts.append({
                'id': row[0],
                'old_phone': row[1],
                'session_file': row[5],
                'ready_time': row[7]
            })
        
        return accounts
    
    def update_status(self, account_id, status, error_message=None):
        """更新账号状态"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE accounts 
            SET status = ?, error_message = ?
            WHERE id = ?
        ''', (status, error_message, account_id))
        
        conn.commit()
        conn.close()
    
    def update_changebind(self, account_id, new_phone, api_url_new):
        """更新换绑信息"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        changebind_time = int(time.time())
        
        c.execute('''
            UPDATE accounts 
            SET new_phone = ?, api_url_new = ?, changebind_time = ?, status = 'completed'
            WHERE id = ?
        ''', (new_phone, api_url_new, changebind_time, account_id))
        
        conn.commit()
        conn.close()
