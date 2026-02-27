"""
知识库基础模块
负责存储和管理用户对话历史、偏好、行为模式等知识
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import Counter
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationRecord:
    """对话记录数据结构"""
    id: Optional[int] = None
    session_id: str = ""
    user_input: str = ""
    ai_response: str = ""
    intent: str = ""
    entities: str = ""  # JSON格式存储
    topic: str = ""
    timestamp: str = ""
    confidence: float = 0.0

@dataclass
class UserPreference:
    """用户偏好数据结构"""
    id: Optional[int] = None
    session_id: str = ""
    intent_type: str = ""
    frequency: int = 0
    last_used: str = ""
    preference_score: float = 0.0

@dataclass
class BehaviorPattern:
    """用户行为模式数据结构"""
    id: Optional[int] = None
    session_id: str = ""
    pattern_type: str = ""  # time_preference, topic_switch, response_style
    pattern_data: str = ""  # JSON格式存储
    frequency: int = 0
    last_observed: str = ""

class KnowledgeBase:
    """知识库核心类"""
    
    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self.init_database()
        logger.info(f"✅ 知识库初始化完成: {db_path}")
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建对话历史表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        intent TEXT,
                        entities TEXT,
                        topic TEXT,
                        timestamp TEXT NOT NULL,
                        confidence REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建用户偏好表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        intent_type TEXT NOT NULL,
                        frequency INTEGER DEFAULT 0,
                        last_used TEXT,
                        preference_score REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(session_id, intent_type)
                    )
                """)
                
                # 创建行为模式表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS behavior_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT,
                        frequency INTEGER DEFAULT 0,
                        last_observed TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建索引以提高查询性能
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON conversation_history(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_intent ON conversation_history(intent)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic ON conversation_history(topic)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversation_history(timestamp)")
                
                conn.commit()
                logger.info("✅ 数据库表结构创建完成")
                
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            raise
    
    def store_conversation(self, session_id: str, user_input: str, ai_response: str, 
                          understanding: Dict) -> bool:
        """存储对话记录"""
        try:
            # 提取理解结果
            intent = understanding.get("intent", "")
            entities = json.dumps(understanding.get("entities", {}), ensure_ascii=False)
            topic = understanding.get("life_context", {}).get("topic_analysis", {}).get("primary_topic", "")
            confidence = understanding.get("confidence", 0.0)
            timestamp = datetime.now().isoformat()
            
            # 使用单个连接处理所有操作
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # 启用WAL模式以提高并发性能
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
                
                cursor = conn.cursor()
                
                # 1. 存储对话记录
                cursor.execute("""
                    INSERT INTO conversation_history 
                    (session_id, user_input, ai_response, intent, entities, topic, timestamp, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (session_id, user_input, ai_response, intent, entities, topic, timestamp, confidence))
                
                # 2. 更新用户偏好（在同一事务中）
                self._update_user_preferences_in_transaction(cursor, session_id, intent, timestamp)
                
                # 3. 分析行为模式（在同一事务中）
                self._analyze_behavior_patterns_in_transaction(cursor, session_id, understanding, timestamp)
                
                # 4. 提交所有更改
                conn.commit()
                logger.info(f"✅ 对话记录存储成功: session_id={session_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 对话记录存储失败: {e}")
            return False
    
    def _update_user_preferences_in_transaction(self, cursor, session_id: str, intent: str, timestamp: str):
        """在事务中更新用户偏好"""
        try:
            # 检查是否已存在该意图的偏好记录
            cursor.execute("""
                SELECT id, frequency FROM user_preferences 
                WHERE session_id = ? AND intent_type = ?
            """, (session_id, intent))
            
            result = cursor.fetchone()
            if result:
                # 更新现有记录
                record_id, frequency = result
                new_frequency = frequency + 1
                preference_score = min(1.0, new_frequency / 10.0)  # 简单的偏好评分
                
                cursor.execute("""
                    UPDATE user_preferences 
                    SET frequency = ?, last_used = ?, preference_score = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_frequency, timestamp, preference_score, record_id))
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO user_preferences 
                    (session_id, intent_type, frequency, last_used, preference_score)
                    VALUES (?, ?, 1, ?, 0.1)
                """, (session_id, intent, timestamp))
                
        except Exception as e:
            logger.error(f"❌ 用户偏好更新失败: {e}")
    
    def _update_user_preferences(self, session_id: str, intent: str, timestamp: str):
        """更新用户偏好（独立方法，用于向后兼容）"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                self._update_user_preferences_in_transaction(cursor, session_id, intent, timestamp)
                conn.commit()
        except Exception as e:
            logger.error(f"❌ 用户偏好更新失败: {e}")
    
    def _analyze_behavior_patterns_in_transaction(self, cursor, session_id: str, understanding: Dict, timestamp: str):
        """在事务中分析用户行为模式"""
        try:
            # 分析时间偏好
            current_hour = datetime.now().hour
            time_pattern = "morning" if 6 <= current_hour < 12 else "afternoon" if 12 <= current_hour < 18 else "evening"
            
            # 分析话题切换模式
            topic_analysis = understanding.get("life_context", {}).get("topic_analysis", {})
            is_topic_switch = topic_analysis.get("is_topic_switch", False)
            
            # 存储时间偏好
            pattern_data = json.dumps({"hour": current_hour, "time_period": time_pattern}, ensure_ascii=False)
            self._store_pattern_in_transaction(cursor, session_id, "time_preference", pattern_data, timestamp)
            
            # 存储话题切换模式
            if is_topic_switch:
                pattern_data = json.dumps({"from_topic": topic_analysis.get("previous_topic", ""), 
                                         "to_topic": topic_analysis.get("primary_topic", "")}, ensure_ascii=False)
                self._store_pattern_in_transaction(cursor, session_id, "topic_switch", pattern_data, timestamp)
                
        except Exception as e:
            logger.error(f"❌ 行为模式分析失败: {e}")
    
    def _analyze_behavior_patterns(self, session_id: str, understanding: Dict, timestamp: str):
        """分析用户行为模式（独立方法，用于向后兼容）"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                self._analyze_behavior_patterns_in_transaction(cursor, session_id, understanding, timestamp)
                conn.commit()
        except Exception as e:
            logger.error(f"❌ 行为模式分析失败: {e}")
    
    def _store_pattern_in_transaction(self, cursor, session_id: str, pattern_type: str, pattern_data: str, timestamp: str):
        """在事务中存储行为模式"""
        cursor.execute("""
            SELECT id, frequency FROM behavior_patterns 
            WHERE session_id = ? AND pattern_type = ?
        """, (session_id, pattern_type))
        
        result = cursor.fetchone()
        if result:
            # 更新现有模式
            record_id, frequency = result
            cursor.execute("""
                UPDATE behavior_patterns 
                SET frequency = ?, last_observed = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (frequency + 1, timestamp, record_id))
        else:
            # 创建新模式
            cursor.execute("""
                INSERT INTO behavior_patterns 
                (session_id, pattern_type, pattern_data, frequency, last_observed)
                VALUES (?, ?, ?, 1, ?)
            """, (session_id, pattern_type, pattern_data, timestamp))
    
    def _store_pattern(self, cursor, session_id: str, pattern_type: str, pattern_data: str, timestamp: str):
        """存储行为模式（独立方法，用于向后兼容）"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                self._store_pattern_in_transaction(cursor, session_id, pattern_type, pattern_data, timestamp)
                conn.commit()
        except Exception as e:
            logger.error(f"❌ 行为模式存储失败: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ConversationRecord]:
        """获取对话历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, user_input, ai_response, intent, entities, topic, timestamp, confidence
                    FROM conversation_history 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (session_id, limit))
                
                records = []
                for row in cursor.fetchall():
                    record = ConversationRecord(
                        id=row[0], session_id=row[1], user_input=row[2], ai_response=row[3],
                        intent=row[4], entities=row[5], topic=row[6], timestamp=row[7], confidence=row[8]
                    )
                    records.append(record)
                
                logger.info(f"✅ 获取对话历史成功: {len(records)}条记录")
                return records
                
        except Exception as e:
            logger.error(f"❌ 获取对话历史失败: {e}")
            return []
    
    def get_user_preferences(self, session_id: str) -> List[UserPreference]:
        """获取用户偏好"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, intent_type, frequency, last_used, preference_score
                    FROM user_preferences 
                    WHERE session_id = ? 
                    ORDER BY preference_score DESC
                """, (session_id,))
                
                preferences = []
                for row in cursor.fetchall():
                    preference = UserPreference(
                        id=row[0], session_id=row[1], intent_type=row[2],
                        frequency=row[3], last_used=row[4], preference_score=row[5]
                    )
                    preferences.append(preference)
                
                logger.info(f"✅ 获取用户偏好成功: {len(preferences)}条记录")
                return preferences
                
        except Exception as e:
            logger.error(f"❌ 获取用户偏好失败: {e}")
            return []
    
    def get_behavior_patterns(self, session_id: str) -> List[BehaviorPattern]:
        """获取用户行为模式"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, pattern_type, pattern_data, frequency, last_observed
                    FROM behavior_patterns 
                    WHERE session_id = ? 
                    ORDER BY frequency DESC
                """, (session_id,))
                
                patterns = []
                for row in cursor.fetchall():
                    pattern = BehaviorPattern(
                        id=row[0], session_id=row[1], pattern_type=row[2],
                        pattern_data=row[3], frequency=row[4], last_observed=row[5]
                    )
                    patterns.append(pattern)
                
                logger.info(f"✅ 获取行为模式成功: {len(patterns)}条记录")
                return patterns
                
        except Exception as e:
            logger.error(f"❌ 获取行为模式失败: {e}")
            return []
    
    def get_knowledge_summary(self, session_id: str) -> Dict[str, Any]:
        """获取知识库摘要（结构化数据）"""
        try:
            # 获取基础统计
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 对话总数
                cursor.execute("SELECT COUNT(*) FROM conversation_history WHERE session_id = ?", (session_id,))
                total_conversations = cursor.fetchone()[0]
                
                # 意图分布
                cursor.execute("""
                    SELECT intent, COUNT(*) as count 
                    FROM conversation_history 
                    WHERE session_id = ? AND intent != '' 
                    GROUP BY intent 
                    ORDER BY count DESC 
                    LIMIT 5
                """, (session_id,))
                intent_distribution = dict(cursor.fetchall())
                
                # 话题分布
                cursor.execute("""
                    SELECT topic, COUNT(*) as count 
                    FROM conversation_history 
                    WHERE session_id = ? AND topic != '' 
                    GROUP BY topic 
                    ORDER BY count DESC 
                    LIMIT 5
                """, (session_id,))
                topic_distribution = dict(cursor.fetchall())
                
                # 用户偏好
                preferences = self.get_user_preferences(session_id)
                top_preferences = [p.intent_type for p in preferences[:3]]
                
                # 行为模式
                patterns = self.get_behavior_patterns(session_id)
                behavior_summary = {}
                for pattern in patterns:
                    if pattern.pattern_type not in behavior_summary:
                        behavior_summary[pattern.pattern_type] = []
                    behavior_summary[pattern.pattern_type].append({
                        "data": pattern.pattern_data,
                        "frequency": pattern.frequency
                    })
                
                summary = {
                    "session_id": session_id,
                    "total_conversations": total_conversations,
                    "intent_distribution": intent_distribution,
                    "topic_distribution": topic_distribution,
                    "top_preferences": top_preferences,
                    "behavior_patterns": behavior_summary,
                    "last_updated": datetime.now().isoformat()
                }
                
                logger.info(f"✅ 获取知识库摘要成功")
                return summary
                
        except Exception as e:
            logger.error(f"❌ 获取知识库摘要失败: {e}")
            return {}

    def get_user_profile_summary_text(self, session_id: str) -> str:
        """
        基于知识库构建一个简短的“用户画像”文本摘要，便于直接放入提示词中。

        内容大致包含：
        - 对话数量
        - 常见意图
        - 常见话题
        - 顶部偏好意图
        - 行为模式的粗略描述
        """
        try:
            summary = self.get_knowledge_summary(session_id)
            if not summary:
                return (
                    "No long-term user profile is available yet. "
                    "You can answer based on general best practices."
                )

            total_conv = summary.get("total_conversations", 0)
            intent_dist = summary.get("intent_distribution", {})
            topic_dist = summary.get("topic_distribution", {})
            top_prefs = summary.get("top_preferences", [])
            behavior_patterns = summary.get("behavior_patterns", {})

            lines = []
            lines.append(f"Total conversations with this user: {total_conv}.")

            if intent_dist:
                intents_str = ", ".join(
                    f"{k} (count={v})" for k, v in intent_dist.items()
                )
                lines.append(f"Most common intents: {intents_str}.")

            if topic_dist:
                topics_str = ", ".join(
                    f"{k} (count={v})" for k, v in topic_dist.items()
                )
                lines.append(f"Most common topics: {topics_str}.")

            if top_prefs:
                prefs_str = ", ".join(top_prefs)
                lines.append(f"Top user preferences by intent: {prefs_str}.")

            # 行为模式更友好地描述一部分常见信息（例如：常在什么时间段对话）
            if behavior_patterns:
                # 时间偏好
                time_items = behavior_patterns.get("time_preference", [])
                time_periods: List[str] = []
                for item in time_items:
                    try:
                        data = json.loads(item.get("data", "{}"))
                        period = data.get("time_period")
                        if period:
                            time_periods.append(period)
                    except Exception:
                        continue

                if time_periods:
                    most_common_period, _ = Counter(time_periods).most_common(1)[0]
                    period_text_map = {
                        "morning": "morning (user often chats in the morning)",
                        "afternoon": "afternoon (user often chats in the afternoon)",
                        "evening": "evening or night (user often chats at night)",
                    }
                    lines.append(
                        f"Typical time preference: {period_text_map.get(most_common_period, most_common_period)}."
                    )

                # 其它模式仅列出类型名称，避免提示过长
                pattern_types = ", ".join(behavior_patterns.keys())
                lines.append(
                    "Observed behavior patterns (types only, details omitted for brevity): "
                    f"{pattern_types}."
                )

            return " ".join(lines) if lines else (
                "No strong user preferences or patterns have been observed yet."
            )
        except Exception as e:
            logger.error(f"❌ 构建用户画像摘要失败: {e}")
            return (
                "User profile summary is temporarily unavailable due to an internal error."
            )
    
    def cleanup_old_records(self, days: int = 30):
        """清理旧记录"""
        try:
            cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 清理旧对话记录
                cursor.execute("DELETE FROM conversation_history WHERE timestamp < ?", (cutoff_date,))
                deleted_conversations = cursor.rowcount
                
                # 清理旧行为模式
                cursor.execute("DELETE FROM behavior_patterns WHERE last_observed < ?", (cutoff_date,))
                deleted_patterns = cursor.rowcount
                
                conn.commit()
                logger.info(f"✅ 清理完成: 删除{deleted_conversations}条对话记录, {deleted_patterns}条行为模式")
                
        except Exception as e:
            logger.error(f"❌ 清理旧记录失败: {e}")


# 全局知识库实例
knowledge_base = KnowledgeBase()

if __name__ == "__main__":
    # 测试知识库功能
    print("🧠 知识库测试开始...")
    
    # 测试存储对话
    test_understanding = {
        "intent": "task_creation",
        "entities": {"task": "写报告", "time": "明天"},
        "confidence": 0.85,
        "life_context": {
            "topic_analysis": {
                "primary_topic": "work",
                "is_topic_switch": False
            }
        }
    }
    
    success = knowledge_base.store_conversation(
        "test_session_001",
        "明天要写报告",
        "好的，我来帮您安排写报告的任务。",
        test_understanding
    )
    
    if success:
        print("✅ 对话存储测试成功")
        
        # 测试获取历史
        history = knowledge_base.get_conversation_history("test_session_001")
        print(f"📝 获取到 {len(history)} 条对话历史")
        
        # 测试获取偏好
        preferences = knowledge_base.get_user_preferences("test_session_001")
        print(f"🎯 获取到 {len(preferences)} 条用户偏好")
        
        # 测试获取摘要
        summary = knowledge_base.get_knowledge_summary("test_session_001")
        print(f"📊 知识库摘要: {summary}")
    else:
        print("❌ 对话存储测试失败")
