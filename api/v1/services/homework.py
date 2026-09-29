"""
作业业务服务
"""
import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from api.v1.models import HomeworkItem, HomeworkRecord

def compare_answers(student: str, correct: str) -> bool:
    """答案比对（数值容差）"""
    if not correct:
        return False
    s = student.strip()
    c = correct.strip()
    if s == c:
        return True
    try:
        if abs(float(s) - float(c)) < 0.01:
            return True
    except ValueError:
        pass
    return False

class HomeworkService:
    """作业业务服务"""
    
    def __init__(self):
        self.data_dir = Path("/opt/data/homework-grader/data")
        self.data_dir.mkdir(exist_ok=True)
        self.storage_file = self.data_dir / "homeworks.json"
        self.load_data()
    
    def load_data(self):
        """加载本地数据"""
        if self.storage_file.exists():
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
        else:
            self.records = []
    
    def save_data(self):
        """保存本地数据"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def get_id(self) -> str:
        """生成唯一 ID"""
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]
    
    def process_upload(self, question_text: str, student_answer: str, correct_answer: str = None) -> HomeworkRecord:
        """处理上传"""
        item = HomeworkItem(
            id=self.get_id(),
            question_text=question_text[:200] if question_text else "未知题目",
            student_answer=student_answer,
            correct_answer=correct_answer,
            is_correct=compare_answers(student_answer, correct_answer) if correct_answer else False
        )
        
        record = HomeworkRecord(
            id=self.get_id(),
            student_name="学生",
            subject="数学",
            items=[item],
            overall_score=100.0 if item.is_correct else 0.0
        )
        
        self.records.append(record)
        self.save_data()
        return record
    
    def check_homework(self, homework_id: str) -> HomeworkRecord:
        """检查作业"""
        for record in self.records:
            if record.id == homework_id:
                for item in record.items:
                    item.is_correct = compare_answers(item.student_answer, item.correct_answer) if item.correct_answer else False
                record.overall_score = sum(1 for i in record.items if i.is_correct) / len(record.items) * 100 if record.items else 0
                record.updated_at = datetime.now()
                self.save_data()
                return record
        return None
    
    def get_wrongbook(self, homework_id: str, include_correct: bool = False) -> List[HomeworkItem]:
        """获取错题本"""
        for record in self.records:
            if record.id == homework_id:
                if include_correct:
                    return record.items
                return [i for i in record.items if not i.is_correct]
        return []
    
    def delete_homework(self, homework_id: str) -> bool:
        """删除作业"""
        for i, record in enumerate(self.records):
            if record.id == homework_id:
                self.records.pop(i)
                self.save_data()
                return True
        return False
