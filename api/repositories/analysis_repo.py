"""分析数据访问"""
from database.connection import BaseRepository, row_to_dict
from typing import Optional


class AnalysisRepository(BaseRepository):
    
    def create_analysis(self, user_id: int, bazi: str,
                        year_pillar: str, month_pillar: str,
                        day_pillar: str, hour_pillar: str,
                        ri_zhu: str, notes: Optional[str] = None) -> int:
        """创建分析记录，返回analysis_id"""
        cur = self.conn.execute("""
            INSERT INTO analyses (user_id, bazi, year_pillar, month_pillar,
                                 day_pillar, hour_pillar, ri_zhu, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, bazi, year_pillar, month_pillar,
              day_pillar, hour_pillar, ri_zhu, notes))
        self.conn.commit()
        return cur.lastrowid
    
    def create_basic_data(self, analysis_id: int,
                          year_data: str, month_data: str,
                          day_data: str, hour_data: str,
                          ri_zhu_gan: str, ri_zhu_wx: str, ri_zhu_yy: str,
                          tian_gan_notes: Optional[str] = None,
                          di_zhi_notes: Optional[str] = None,
                          cheng_gu_weight: Optional[str] = None,
                          cheng_gu_comment: Optional[str] = None) -> int:
        """创建基础数据记录"""
        cur = self.conn.execute("""
            INSERT INTO basic_data (analysis_id, year_data, month_data, day_data, hour_data,
                                   ri_zhu_gan, ri_zhu_wx, ri_zhu_yy,
                                   tian_gan_notes, di_zhi_notes,
                                   cheng_gu_weight, cheng_gu_comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (analysis_id, year_data, month_data, day_data, hour_data,
              ri_zhu_gan, ri_zhu_wx, ri_zhu_yy,
              tian_gan_notes, di_zhi_notes,
              cheng_gu_weight, cheng_gu_comment))
        self.conn.commit()
        return cur.lastrowid
    
    def create_analysis_results(self, analysis_id: int,
                                shen_qiang_ruo: Optional[str] = None,
                                cai_xing: Optional[str] = None,
                                ge_ju: Optional[str] = None,
                                xi_yong_shen: Optional[str] = None,
                                energy: Optional[str] = None,
                                da_yun: Optional[str] = None,
                                dimensions: Optional[str] = None) -> int:
        """创建分析结果记录"""
        cur = self.conn.execute("""
            INSERT INTO analysis_results (analysis_id, shen_qiang_ruo, cai_xing,
                                         ge_ju, xi_yong_shen, energy,
                                         da_yun, dimensions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (analysis_id, shen_qiang_ruo, cai_xing,
              ge_ju, xi_yong_shen, energy,
              da_yun, dimensions))
        self.conn.commit()
        return cur.lastrowid
    
    def update_status(self, analysis_id: int, status: str,
                      error_message: Optional[str] = None):
        """更新分析状态"""
        if error_message:
            self.conn.execute("""
                UPDATE analyses SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, error_message, analysis_id))
        else:
            self.conn.execute("""
                UPDATE analyses SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, analysis_id))
        self.conn.commit()
    
    def get_analysis(self, analysis_id: int) -> Optional[dict]:
        """获取完整分析数据"""
        analysis = self.conn.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()
        if not analysis:
            return None
        
        result = dict(analysis)
        
        # 关联基础数据
        bd = self.conn.execute(
            "SELECT * FROM basic_data WHERE analysis_id = ?", (analysis_id,)
        ).fetchone()
        result['basic_data'] = dict(bd) if bd else None
        
        # 关联分析结果
        ar = self.conn.execute(
            "SELECT * FROM analysis_results WHERE analysis_id = ?", (analysis_id,)
        ).fetchone()
        result['analysis_results'] = dict(ar) if ar else None
        
        return result
    
    def get_user_analyses(self, user_id: int, limit: int = 20) -> list[dict]:
        cur = self.conn.execute("""
            SELECT * FROM analyses WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT ?
        """, (user_id, limit))
        return [dict(r) for r in cur.fetchall()]
