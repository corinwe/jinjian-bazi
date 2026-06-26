"""用户数据访问"""
from database.connection import BaseRepository, row_to_dict
from typing import Optional


class UserRepository(BaseRepository):
    
    def create(self, name: str, gender: str,
               birth_year: int, birth_month: int, birth_day: int,
               birth_hour: int = 0, birth_minute: int = 0,
               calendar_type: str = "solar",
               lunar_month: Optional[int] = None,
               lunar_day: Optional[int] = None,
               tags: Optional[str] = None) -> int:
        """创建用户，返回user_id"""
        cur = self.conn.execute("""
            INSERT INTO users (name, gender, birth_year, birth_month, birth_day,
                              birth_hour, birth_minute, calendar_type,
                              lunar_month, lunar_day, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, gender, birth_year, birth_month, birth_day,
              birth_hour, birth_minute, calendar_type,
              lunar_month, lunar_day, tags))
        self.conn.commit()
        return cur.lastrowid
    
    def find_by_id(self, user_id: int) -> Optional[dict]:
        cur = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return row_to_dict(cur.fetchone())
    
    def find_by_exact_match(self, name: str, gender: str,
                            birth_year: int, birth_month: int, birth_day: int,
                            birth_hour: int) -> Optional[dict]:
        """按精确出生信息查找已有用户"""
        cur = self.conn.execute("""
            SELECT * FROM users 
            WHERE name = ? AND gender = ? 
              AND birth_year = ? AND birth_month = ? AND birth_day = ?
              AND birth_hour = ?
            ORDER BY id DESC LIMIT 1
        """, (name, gender, birth_year, birth_month, birth_day, birth_hour))
        return row_to_dict(cur.fetchone())
