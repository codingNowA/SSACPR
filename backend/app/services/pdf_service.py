"""
简历PDF生成服务
"""
import io
import json
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import logging

logger = logging.getLogger(__name__)


class ResumePDFGenerator:
    """简历PDF生成器"""

    def __init__(self):
        """初始化PDF生成器，注册中文字体"""
        try:
            # 使用reportlab内置的中文字体支持
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            self.font_name = 'STSong-Light'
            logger.info("使用STSong-Light中文字体")
        except Exception as e:
            logger.warning(f"注册中文字体失败: {e}，将使用Helvetica")
            self.font_name = 'Helvetica'

    def generate_resume_pdf(self, parsed_data: dict, version_name: str) -> bytes:
        """
        生成简历PDF

        Args:
            parsed_data: 简历结构化数据
            version_name: 版本名称

        Returns:
            PDF文件的字节数据
        """
        buffer = io.BytesIO()

        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # 构建文档内容
        story = []
        styles = getSampleStyleSheet()

        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName=self.font_name
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=8,
            spaceBefore=12,
            fontName=self.font_name
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName=self.font_name
        )

        # 版本标题
        story.append(Paragraph(f"简历 - {version_name}", title_style))
        story.append(Spacer(1, 0.5*cm))

        # 基本信息
        basic_info = parsed_data.get('basic_info', {})
        if basic_info:
            story.append(Paragraph("基本信息", heading_style))

            info_data = []
            if basic_info.get('name'):
                info_data.append(['姓名:', basic_info['name']])
            if basic_info.get('phone'):
                info_data.append(['电话:', basic_info['phone']])
            if basic_info.get('email'):
                info_data.append(['邮箱:', basic_info['email']])
            if basic_info.get('job_intention'):
                info_data.append(['求职意向:', basic_info['job_intention']])
            if basic_info.get('age'):
                info_data.append(['年龄:', str(basic_info['age'])])
            if basic_info.get('gender'):
                info_data.append(['性别:', basic_info['gender']])
            if basic_info.get('location'):
                info_data.append(['所在地:', basic_info['location']])

            if info_data:
                table = Table(info_data, colWidths=[3*cm, 14*cm])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))

        # 教育经历
        education = parsed_data.get('education', [])
        if education:
            story.append(Paragraph("教育经历", heading_style))
            for edu in education:
                school = edu.get('school', '')
                major = edu.get('major', '')
                degree = edu.get('degree', '')
                start_date = edu.get('start_date', '')
                end_date = edu.get('end_date', '')
                gpa = edu.get('gpa', '')
                description = edu.get('description', '')

                text = f"<b>{school}</b>"
                if major:
                    text += f" · {major}"
                if degree:
                    text += f" · {degree}"
                if start_date or end_date:
                    text += f"<br/><font color='grey'>{start_date} - {end_date}</font>"
                if gpa:
                    text += f"<br/>GPA: {gpa}"
                if description:
                    text += f"<br/>{description}"

                story.append(Paragraph(text, body_style))
            story.append(Spacer(1, 0.3*cm))

        # 工作经历
        work_experience = parsed_data.get('work_experience', [])
        if work_experience:
            story.append(Paragraph("工作经历", heading_style))
            for work in work_experience:
                company = work.get('company', '')
                position = work.get('position', '')
                start_date = work.get('start_date', '')
                end_date = work.get('end_date', '')
                description = work.get('description', '')
                achievements = work.get('achievements', [])

                text = f"<b>{company}</b>"
                if position:
                    text += f" · {position}"
                if start_date or end_date:
                    text += f"<br/><font color='grey'>{start_date} - {end_date}</font>"
                if description:
                    text += f"<br/>{description}"

                story.append(Paragraph(text, body_style))

                # 添加成果列表
                if achievements:
                    for achievement in achievements:
                        story.append(Paragraph(f"• {achievement}", body_style))

                story.append(Spacer(1, 0.2*cm))

        # 项目经验
        project_experience = parsed_data.get('project_experience', [])
        if project_experience:
            story.append(Paragraph("项目经验", heading_style))
            for project in project_experience:
                name = project.get('name', '')
                role = project.get('role', '')
                start_date = project.get('start_date', '')
                end_date = project.get('end_date', '')
                description = project.get('description', '')
                tech_stack = project.get('tech_stack', [])
                achievements = project.get('achievements', [])

                text = f"<b>{name}</b>"
                if role:
                    text += f" · {role}"
                if start_date or end_date:
                    text += f"<br/><font color='grey'>{start_date} - {end_date}</font>"
                if description:
                    text += f"<br/>{description}"

                # 添加技术栈
                if tech_stack:
                    tech_text = ' · '.join(tech_stack)
                    text += f"<br/><font color='blue'>技术栈: {tech_text}</font>"

                story.append(Paragraph(text, body_style))

                # 添加成果列表
                if achievements:
                    for achievement in achievements:
                        story.append(Paragraph(f"• {achievement}", body_style))

                story.append(Spacer(1, 0.2*cm))

        # 技能特长
        skills = parsed_data.get('skills', [])
        if skills:
            story.append(Paragraph("技能特长", heading_style))
            # 处理 skills 可能是字符串列表或 SkillTag 对象列表
            skill_names = []
            for s in skills:
                if isinstance(s, str):
                    skill_names.append(s)
                elif isinstance(s, dict):
                    skill_names.append(s.get('name', str(s)))
                else:
                    skill_names.append(str(s))
            skills_text = ' · '.join(skill_names) if skill_names else ''
            if skills_text:
                story.append(Paragraph(skills_text, body_style))
            story.append(Spacer(1, 0.3*cm))

        # 构建PDF
        doc.build(story)

        # 获取PDF数据
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data

    def generate_resume_pdf_with_diagnosis(self, parsed_data: dict, scores: dict, version_name: str, optimization: dict = None) -> bytes:
        """
        生成包含诊断结果的简历PDF

        Args:
            parsed_data: 简历结构化数据
            scores: 诊断评分结果
            version_name: 版本名称
            optimization: 优化建议数据（可选）

        Returns:
            PDF文件的字节数据
        """
        buffer = io.BytesIO()

        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # 构建文档内容
        story = []
        styles = getSampleStyleSheet()

        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName=self.font_name
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=8,
            spaceBefore=12,
            fontName=self.font_name
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName=self.font_name
        )

        small_style = ParagraphStyle(
            'CustomSmall',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            textColor=colors.grey,
            fontName=self.font_name
        )

        # 版本标题
        story.append(Paragraph(f"简历 - {version_name}", title_style))
        story.append(Spacer(1, 0.3*cm))

        # ===== 诊断结果概览 =====
        story.append(Paragraph("诊断结果", heading_style))

        # 提取评分数据（兼容嵌套格式）
        def get_score(data, key):
            """提取评分，兼容嵌套对象和直接数值"""
            val = data.get(key, 0)
            if isinstance(val, dict):
                return val.get('total_score', 0)
            return val if isinstance(val, (int, float)) else 0

        # 综合评分
        total_score = get_score(scores, 'total_score')
        score_color = self._get_score_color(total_score)
        story.append(Paragraph(
            f"<font color='{score_color}'><b>综合评分: {total_score}/100</b></font>",
            body_style
        ))
        story.append(Spacer(1, 0.2*cm))

        # 各维度评分表格
        score_data = [['维度', '得分']]
        score_items = [
            ('完整性', get_score(scores, 'completeness')),
            ('专业性', get_score(scores, 'professionalism')),
            ('量化程度', get_score(scores, 'quantification')),
            ('项目深度', get_score(scores, 'project_depth')),
            ('岗位匹配', get_score(scores, 'job_match')),
        ]

        for label, score in score_items:
            if score > 0:  # 只显示有分数的维度
                score_data.append([label, f"{score}/100"])

        if len(score_data) > 1:  # 如果有数据才显示表格
            score_table = Table(score_data, colWidths=[8*cm, 6*cm])
            score_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(score_table)
            story.append(Spacer(1, 0.5*cm))

        # 改进建议（从dimensions中提取）
        dimensions = scores.get('dimensions', [])
        if dimensions:
            story.append(Paragraph("改进建议", heading_style))
            for i, dim in enumerate(dimensions[:5], 1):  # 最多显示5条
                feedback = dim.get('feedback', '')
                if feedback:
                    story.append(Paragraph(f"{i}. {feedback}", body_style))
            story.append(Spacer(1, 0.5*cm))

        # 详细优化建议（从 optimization.general_suggestions 中提取）
        if optimization and optimization.get('general_suggestions'):
            story.append(Paragraph("详细优化建议", heading_style))
            general_suggestions = optimization['general_suggestions']

            for i, suggestion in enumerate(general_suggestions[:8], 1):  # 最多显示8条
                # 优先级标签
                priority = suggestion.get('priority', '中')
                priority_colors = {'高': '#f5222d', '中': '#fa8c16', '低': '#1890ff'}
                priority_color = priority_colors.get(priority, '#1890ff')

                # 标题和优先级
                title_text = f"<font color='{priority_color}'>[{priority}]</font> <b>{suggestion.get('title', '')}</b>"
                story.append(Paragraph(title_text, body_style))

                # 类别和说明
                category = suggestion.get('category', '')
                description = suggestion.get('description', '')
                if category or description:
                    info_text = f"类别: {category} | {description}" if category else description
                    story.append(Paragraph(info_text, small_style))

                # 当前内容
                current_content = suggestion.get('current_content')
                if current_content and current_content != '无':
                    story.append(Paragraph("<font color='#666'>当前内容:</font>", small_style))
                    story.append(Paragraph(f"<font color='#d32f2f'>{current_content}</font>", body_style))

                # 建议内容
                suggested_content = suggestion.get('suggested_content', '')
                if suggested_content:
                    story.append(Paragraph("<font color='#666'>建议修改为:</font>", small_style))
                    story.append(Paragraph(f"<font color='#388e3c'>{suggested_content}</font>", body_style))

                # 原因
                reason = suggestion.get('reason', '')
                if reason:
                    story.append(Paragraph(f"<font color='#666'>原因: {reason}</font>", small_style))

                story.append(Spacer(1, 0.3*cm))

            story.append(Spacer(1, 0.3*cm))

        # 分隔线
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("<hr/>", body_style))
        story.append(Spacer(1, 0.5*cm))

        # ===== 简历内容 =====
        story.append(Paragraph("简历内容", heading_style))

        # 基本信息
        basic_info = parsed_data.get('basic_info', {})
        if basic_info:
            story.append(Paragraph("基本信息", heading_style))

            info_data = []
            if basic_info.get('name'):
                info_data.append(['姓名:', basic_info['name']])
            if basic_info.get('phone'):
                info_data.append(['电话:', basic_info['phone']])
            if basic_info.get('email'):
                info_data.append(['邮箱:', basic_info['email']])
            if basic_info.get('job_intention'):
                info_data.append(['求职意向:', basic_info['job_intention']])
            if basic_info.get('age'):
                info_data.append(['年龄:', str(basic_info['age'])])
            if basic_info.get('gender'):
                info_data.append(['性别:', basic_info['gender']])
            if basic_info.get('location'):
                info_data.append(['所在地:', basic_info['location']])

            if info_data:
                table = Table(info_data, colWidths=[3*cm, 14*cm])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))

        # 教育经历
        education = parsed_data.get('education', [])
        if education:
            story.append(Paragraph("教育经历", heading_style))
            for edu in education:
                school = edu.get('school', '')
                major = edu.get('major', '')
                degree = edu.get('degree', '')
                start_date = edu.get('start_date', '')
                end_date = edu.get('end_date', '')
                gpa = edu.get('gpa', '')
                description = edu.get('description', '')

                text = f"<b>{school}</b>"
                if major:
                    text += f" · {major}"
                if degree:
                    text += f" · {degree}"
                if start_date or end_date:
                    text += f"<br/><font color='grey'>{start_date} - {end_date}</font>"
                if gpa:
                    text += f"<br/>GPA: {gpa}"
                if description:
                    text += f"<br/>{description}"

                story.append(Paragraph(text, body_style))
            story.append(Spacer(1, 0.3*cm))

        # 工作经历
        work_experience = parsed_data.get('work_experience', [])
        if work_experience:
            story.append(Paragraph("工作经历", heading_style))
            for work in work_experience:
                company = work.get('company', '')
                position = work.get('position', '')
                start_date = work.get('start_date', '')
                end_date = work.get('end_date', '')
                description = work.get('description', '')
                achievements = work.get('achievements', [])

                text = f"<b>{company}</b>"
                if position:
                    text += f" · {position}"
                if start_date or end_date:
                    text += f"<br/><font color='grey'>{start_date} - {end_date}</font>"
                if description:
                    text += f"<br/>{description}"

                story.append(Paragraph(text, body_style))

                # 添加成果列表
                if achievements:
                    for achievement in achievements:
                        story.append(Paragraph(f"• {achievement}", body_style))

                story.append(Spacer(1, 0.2*cm))

        # 项目经验
        project_experience = parsed_data.get('project_experience', [])
        if project_experience:
            story.append(Paragraph("项目经验", heading_style))
            for project in project_experience:
                name = project.get('name', '')
                role = project.get('role', '')
                start_date = project.get('start_date', '')
                end_date = project.get('end_date', '')
                description = project.get('description', '')
                tech_stack = project.get('tech_stack', [])
                achievements = project.get('achievements', [])

                text = f"<b>{name}</b>"
                if role:
                    text += f" · {role}"
                if start_date or end_date:
                    text += f"<br/><font color='grey'>{start_date} - {end_date}</font>"
                if description:
                    text += f"<br/>{description}"

                # 添加技术栈
                if tech_stack:
                    tech_text = ' · '.join(tech_stack)
                    text += f"<br/><font color='blue'>技术栈: {tech_text}</font>"

                story.append(Paragraph(text, body_style))

                # 添加成果列表
                if achievements:
                    for achievement in achievements:
                        story.append(Paragraph(f"• {achievement}", body_style))

                story.append(Spacer(1, 0.2*cm))

        # 技能特长
        skills = parsed_data.get('skills', [])
        if skills:
            story.append(Paragraph("技能特长", heading_style))
            skill_names = []
            for s in skills:
                if isinstance(s, str):
                    skill_names.append(s)
                elif isinstance(s, dict):
                    skill_names.append(s.get('name', str(s)))
                else:
                    skill_names.append(str(s))
            skills_text = ' · '.join(skill_names) if skill_names else ''
            if skills_text:
                story.append(Paragraph(skills_text, body_style))
            story.append(Spacer(1, 0.3*cm))

        # 自我评价
        self_evaluation = parsed_data.get('self_evaluation', '')
        if self_evaluation:
            story.append(Paragraph("自我评价", heading_style))
            story.append(Paragraph(self_evaluation, body_style))

        # 构建PDF
        doc.build(story)

        # 获取PDF数据
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data

    def _get_score_color(self, score: float) -> str:
        """根据分数返回颜色"""
        if score >= 90:
            return '#52c41a'  # 绿色
        elif score >= 80:
            return '#1890ff'  # 蓝色
        elif score >= 70:
            return '#faad14'  # 橙色
        elif score >= 60:
            return '#fa8c16'  # 深橙色
        else:
            return '#f5222d'  # 红色


# 全局实例
pdf_generator = ResumePDFGenerator()
