import os
import random
from datetime import datetime
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4

def generate_ticket_pdf(student_name, exam_name, exam_date, ticket_number):
    """生成准考证PDF并返回保存路径"""
    # 注册 reportlab 内置中文字体
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    
    # 确保存储目录存在
    ticket_dir = os.path.join(settings.MEDIA_ROOT, 'tickets')
    if not os.path.exists(ticket_dir):
        os.makedirs(ticket_dir)
        
    filename = f"ticket_{ticket_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(ticket_dir, filename)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # 绘制准考证内容
    c.setFont('STSong-Light', 24)
    c.drawCentredString(width / 2.0, height - 100, "考试准考证")
    
    c.setFont('STSong-Light', 16)
    c.drawString(100, height - 180, f"考生姓名：{student_name}")
    c.drawString(100, height - 220, f"准考证号：{ticket_number}")
    c.drawString(100, height - 260, f"考试科目：{exam_name}")
    c.drawString(100, height - 300, f"考试时间：{exam_date}")
    
    c.setFont('STSong-Light', 12)
    c.drawString(100, height - 400, "考生须知：")
    c.drawString(100, height - 430, "1. 请提前15分钟到达考场。")
    c.drawString(100, height - 460, "2. 请携带有效身份证件及本准考证。")
    c.drawString(100, height - 490, "3. 考试期间严禁作弊。")
    
    c.save()
    
    return f"tickets/{filename}"

def generate_ticket_number():
    """生成20位随机准考证号"""
    return f"{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100000, 999999)}"