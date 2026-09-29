"""
API 路由
"""
from fastapi import APIRouter
from typing import Optional

from pydantic import BaseModel

from api.v1.models import HomeworkRecord, HomeworkItem
from api.v1.services.homework import HomeworkService

# 定义请求模型
class UploadRequest(BaseModel):
    question_text: str = "未知题目"
    student_answer: str = ""
    correct_answer: Optional[str] = None

class CheckRequest(BaseModel):
    homework_id: str

router = APIRouter()
homework_service = HomeworkService()

@router.post("/upload", response_model=HomeworkRecord)
def upload_homework(request: UploadRequest):
    """
    上传作业（模拟 OCR 识别结果）
    JSON body: {"question_text": "...", "student_answer": "...", "correct_answer": "..."}
    """
    return homework_service.process_upload(request.question_text, request.student_answer, request.correct_answer)

@router.post("/check", response_model=HomeworkRecord)
def check_homework(request: CheckRequest):
    """
    检查作业答案
    JSON body: {"homework_id": "..."}
    """
    if not request.homework_id:
        return {"error": "缺少 homework_id"}
    return homework_service.check_homework(request.homework_id)

@router.get("/wrongbook")
def get_wrongbook(homework_id: str = None, include_correct: bool = False):
    """
    获取错题本
    query params: homework_id, include_correct
    """
    if not homework_id:
        return {"error": "缺少 homework_id"}
    items = homework_service.get_wrongbook(homework_id, include_correct)
    return {"items": items, "count": len(items)}

@router.get("/homeworks")
def list_homeworks():
    """
    获取所有作业列表
    """
    records = homework_service.get_all_records()
    return {"records": records, "count": len(records)}

@router.get("/report/pdf")
def generate_report(homework_id: str, student_name: str = "学生"):
    """
    生成 PDF 错题报告
    query params: homework_id, student_name
    Returns base64 encoded PDF
    """
    import base64
    items = homework_service.get_wrongbook(homework_id, include_correct=False)
    if not items:
        return {"message": "没有错题"}, 200
    
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="错题报告")
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph(f"<b style='font-size: 18pt;'>错题报告</b> - {student_name}", styles['Heading1'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    for item in items:
        q = item.question_text[:80] if item.question_text else "未知题目"
        a = item.student_answer or "未作答"
        status = "✅ 正确" if item.is_correct else "❌ 错误"
        style = styles['Normal'] if item.is_correct else styles['Warning']
        p = Paragraph(f"<b>题目:</b> {q}<br/><br/><b>你的答案:</b> {a}<br/><br/><b>状态:</b> {status}", style)
        story.append(p)
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    pdf_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return {"pdf": pdf_base64}, 200, {"Content-Disposition": "attachment; filename=错题报告.pdf"}
