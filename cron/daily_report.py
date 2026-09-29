"""
定时任务：每晚 8 点生成 PDF 报告并发送邮件
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
from pathlib import Path

from api.v1.services.homework import HomeworkService

def generate_pdf_report(student_name, items):
    """生成 PDF 错题报告"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        # 这里简化实现，实际需要完整的 PDF 生成逻辑
        return f"""
        ========== 错题报告：{student_name} ==========
        日期：{datetime.now().strftime('%Y-%m-%d')}
        
        错题数量：{len(items)}
        
        """ + "\n\n".join([
            f"题目：{item.question_text}\n学生答案：{item.student_answer}\n\n"
            for item in items
        ]) + """
        
        错题不是敌人，而是帮你变强的秘密武器 💪
        明天继续加油！🌟
        """
    except ImportError as e:
        print(f"PDF 生成依赖缺失：{e}")
        return ""

def send_email(to, subject, body):
    """发送邮件"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        mail_host = os.getenv("MAIL_HOST", "smtp.163.com")
        mail_user = os.getenv("MAIL_USER")
        mail_password = os.getenv("MAIL_PASSWORD")
        
        if not mail_user or not mail_password:
            print("邮件配置不完整，跳过发送")
            return
        
        msg = MIMEMultipart()
        msg['From'] = mail_user
        msg['To'] = to
        msg['Subject'] = subject
        
        # 使用 HTML 格式
        msg.attach(MIMEText(body, 'html', _charset='utf-8'))
        
        server = smtplib.SMTP(mail_host, 587)
        server.starttls()
        server.login(mail_user, mail_password)
        server.send_message(msg)
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败：{e}")

def daily_report_task():
    """每日错题报告任务"""
    print(f"=== 每日错题报告任务开始：{datetime.now()} ===")
    
    service = HomeworkService()
    
    # 获取今天的所有错题
    today = datetime.now().date()
    wrong_items = []
    
    for record in service.records:
        for item in record.items:
            if not item.is_correct:
                wrong_items.append({
                    'student': record.student_name,
                    'date': record.date,
                    'question': item.question_text,
                    'answer': item.student_answer
                })
    
    if not wrong_items:
        print("今日无错题，无需生成报告")
        return
    
    # 生成报告内容
    report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }}
            .encourage {{ background: #e8f5e9; padding: 15px; margin-top: 20px; border-radius: 8px; color: #4caf50; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>📚 每日错题报告</h2>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="content">
            <h3>学生：{wrong_items[0]['student']}</h3>
            <p>今日错题数量：{len(wrong_items)}</p>
        </div>
    """
    
    for item in wrong_items:
        report += f"""
            <div class="item">
                <strong>题目：</strong>{item['question']}\n
                <strong>你的答案：</strong>{item['answer']}\n
            </div>
        """
    
    report += """
        <div class="encourage">
            <h3>🌟 太棒了！又攻克了这么多难题！</h3>
            <p>错题不是敌人，而是帮你变强的秘密武器 💪</p>
            <p>明天继续加油！你一定能越来越棒！</p>
        </div>
    </body>
    </html>
    """
    
    # 发送邮件
    to_email = os.getenv("MAIL_USER")
    if to_email:
        subject = f"【错题日报】{wrong_items[0]['student']} - {datetime.now().strftime('%Y-%m-%d')}"
        send_email(to_email, subject, report)
    
    print(f"=== 每日错题报告任务结束，共 {len(wrong_items)} 道错题 ===")

def main():
    """启动定时任务"""
    scheduler = BackgroundScheduler()
    
    # 设置每晚 8 点执行
    scheduler.add_job(
        daily_report_task,
        'cron',
        hour=20,
        minute=0,
        id='daily_wrongbook_report'
    )
    
    print("定时任务已启动，每晚 20:00 自动执行")
    scheduler.start()
    
    # 保留主进程
    import time
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    main()
