"""
数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    CHOICE = "choice"      # 选择题
    FILL = "fill"          # 填空题
    SHORT = "short"       # 简答题

class HomeworkItem(BaseModel):
    """单道题目记录"""
    id: str = Field(default_factory=lambda: str(hash(datetime.now().timestamp())))
    question_text: str = Field(..., description="识别后的题目文本")
    question_image: Optional[str] = Field(None, description="图片 URL 或文件名")
    answer_type: QuestionType = QuestionType.FILL
    student_answer: str = Field(..., description="学生作答")
    correct_answer: Optional[str] = Field(None, description="参考答案")
    is_correct: bool = Field(default=False, description="判断结果")
    analysis: str = Field(default="", description="解析内容")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class HomeworkRecord(BaseModel):
    """完整作业记录"""
    id: str = Field(default_factory=lambda: str(hash(datetime.now().timestamp())))
    student_name: str = Field(default="未命名学生")
    subject: str = Field(default="数学")
    date: datetime = Field(default_factory=datetime.now)
    items: List[HomeworkItem] = Field(default_factory=list)
    overall_score: Optional[float] = Field(None, description="总分")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UploadRequest(BaseModel):
    """上传请求"""
    file: bytes = Field(..., description="图片二进制数据")
    student_name: str = Field(default="未命名学生")
    subject: str = Field(default="数学")

class CheckRequest(BaseModel):
    """检查请求（补充答案）"""
    homework_id: str
    item_ids: List[str]
    correct_answers: dict = Field(default_factory=dict, description="{item_id: correct_answer}")

class WrongbookRequest(BaseModel):
    """错题本请求"""
    homework_id: str
    include_correct: bool = Field(default=False, description="是否包含正确题目")
