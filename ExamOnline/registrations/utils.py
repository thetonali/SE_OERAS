# registrations/utils.py
import os
import uuid
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

def generate_admission_ticket_pdf(user_name, exam_name, ticket_number):
    """
    生成准考证PDF文件，返回相对于 media 的文件路径
    """
    # 确保 media/tickets 目录存在
    media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
    ticket_dir = os.path.join(media_root, 'tickets')
    if not os.path.exists(ticket_dir):
        os.makedirs(ticket_dir)

    # 生成唯一文件名
    filename = f"ticket_{ticket_number}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(ticket_dir, filename)

    # 注册中文字体 (这里以系统自带的黑体为例，如果部署到Linux报错，请将 simhei.ttf 放入项目目录并修改此处路径)
    try:
        pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
        font_name = 'SimHei'
    except Exception:
        # 如果找不到黑体，尝试注册一个通用中文字体路径，需根据实际系统环境调整
        try:
            pdfmetrics.registerFont(TTFont('SimSun', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'))
            font_name = 'SimSun'
        except Exception:
            font_name = 'Helvetica' # 降级为默认字体（不支持中文）

    # 初始化 Canvas
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # 绘制准考证内容
    c.setFont(font_name, 24)
    c.drawCentredString(width / 2.0, height - 100, "考 生 准 考 证")

    c.setFont(font_name, 14)
    c.drawString(100, height - 180, f"考生姓名：{user_name}")
    c.drawString(100, height - 220, f"准考证号：{ticket_number}")
    c.drawString(100, height - 260, f"考试名称：{exam_name}")
    
    # 绘制分割线和注意事项
    c.line(100, height - 300, width - 100, height - 300)
    c.setFont(font_name, 12)
    c.drawString(100, height - 340, "注意事项：")
    c.drawString(100, height - 370, "1. 请携带本人有效身份证件及本准考证按时参加考试。")
    c.drawString(100, height - 400, "2. 考试期间请严格遵守考场纪律，作弊者将取消成绩。")

    c.showPage()
    c.save()

    # 返回相对路径以便存入数据库
    return f"tickets/{filename}"