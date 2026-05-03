<!-- exam-online/src/views/TicketDownload.vue -->
<template>
    <div class="ticket-download">
        <!-- 原有的界面结构 -->
        <el-card>
            <div slot="header">
                <span>我的准考证</span>
            </div>
            <el-table :data="tickets" style="width: 100%" v-loading="loading">
                <el-table-column prop="registration_info.exam_info.name" label="考试名称" width="250"></el-table-column>
                <el-table-column prop="ticket_number" label="准考证号" width="200"></el-table-column>
                <el-table-column label="生成时间" width="200">
                    <template slot-scope="scope">
                        {{ formatDate(scope.row.generate_time) }}
                    </template>
                </el-table-column>
                <el-table-column label="操作">
                    <template slot-scope="scope">
                        <!-- 修改了点击事件，传入整行数据用于生成PDF -->
                        <el-button size="small" type="primary" icon="el-icon-download" @click="downloadPDF(scope.row)">
                            下载 PDF
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <!-- 隐藏的准考证模板，仅用于渲染生成 PDF，不会显示在界面上 -->
        <div class="ticket-template-container">
            <div ref="ticketPrintArea" class="ticket-print-area">
                <div class="ticket-header">
                    <h2>考试准考证</h2>
                </div>
                <div class="ticket-content">
                    <p><strong>考生姓名：</strong><span>{{ candidateName }}</span></p>
                    <p><strong>性别：</strong><span>{{ candidateGender }}</span></p>
                    <p><strong>准考证号：</strong><span>{{ currentTicket.ticket_number }}</span></p>
                    <p><strong>考试名称：</strong><span>{{ currentTicket.name }}</span></p>
                    <p><strong>考试日期：</strong><span>{{ currentTicket.exam_time }}</span></p>
                    <p><strong>考试时长：</strong><span>{{ currentTicket.duration }}</span></p>
                    <p><strong>打印日期：</strong><span>{{ currentDate }}</span></p>
                </div>
                <div class="ticket-footer">
                    <p>注意事项：请考生携带本准考证和有效身份证件按时参加考试，严禁携带违纪物品进入考场。</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
// 引入生成 PDF 所需的库
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

export default {
    name: "TicketDownload",
    data() {
        return {
            tickets: [],
            loading: false,
            // 考生姓名，您可以在此填写或修改为动态获取
            candidateName: this.$store.state.student.name, 
            // 考生性别
            candidateGender: this.$store.state.student.gender=='m' ? '男' : '女',
            // 用于临时存放当前正在生成PDF的准考证数据
            currentTicket: {
                name: "",
                ticket_number: "",
                exam_time: "",
                duration: ""
            }
        }
    },
    computed: {
        // 动态获取当前日期
        currentDate() {
            const date = new Date();
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}年${month}月${day}日`;
        }
    },
    created() {
        this.fetchTickets();
    },
    methods: {
        fetchTickets() {
            this.loading = true;
            
            // 模拟加载效果，硬编码图片中的四条考试信息及所需的元数据
            setTimeout(() => {
                this.tickets = [
                    {
                        registration_info: { exam_info: { name: "四级考试（1）" } },
                        ticket_number: "202003030001",
                        generate_time: "2020-02-25T10:00:00",
                        exam_time: "2020-03-03",
                        duration: "120分钟"
                    },
                    {
                        registration_info: { exam_info: { name: "四级考试（2）" } },
                        ticket_number: "202003040002",
                        generate_time: "2020-02-26T10:00:00",
                        exam_time: "2020-03-04",
                        duration: "120分钟"
                    },
                    {
                        registration_info: { exam_info: { name: "六级考试（1）" } },
                        ticket_number: "202003080001",
                        generate_time: "2020-03-01T10:00:00",
                        exam_time: "2020-03-08",
                        duration: "120分钟"
                    },
                    {
                        registration_info: { exam_info: { name: "六级考试（2）" } },
                        ticket_number: "202004060002",
                        generate_time: "2020-03-25T10:00:00",
                        exam_time: "2020-04-06",
                        duration: "120分钟"
                    }
                ];
                this.loading = false;
            }, 300);
        },
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString();
        },
        async downloadPDF(row) {
            // 将当前行的数据赋值给模板绑定的变量
            this.currentTicket = {
                name: row.registration_info.exam_info.name,
                ticket_number: row.ticket_number,
                exam_time: row.exam_time,
                duration: row.duration
            };

            // 开启表格的 loading 状态以防止重复点击
            this.loading = true;

            try {
                // 等待 Vue 将刚刚赋值的 currentTicket 渲染到隐藏的 DOM 中
                await this.$nextTick();

                // 获取要生成 PDF 的 DOM 元素
                const element = this.$refs.ticketPrintArea;

                // 使用 html2canvas 将 DOM 转换为 Canvas 图片
                const canvas = await html2canvas(element, {
                    scale: 2, // 放大比例，保证生成的 PDF 清晰度
                    useCORS: true,
                    backgroundColor: '#ffffff'
                });

                // 将 Canvas 转换为 Base64 图片数据
                const imgData = canvas.toDataURL('image/jpeg', 1.0);

                // 创建 JS-PDF 实例 (p: 纵向, pt: 像素点, a4: 纸张大小)
                const pdf = new jsPDF('p', 'pt', 'a4');

                // 计算图片放入 A4 纸时的自适应宽高
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

                // 将图片写入 PDF
                pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);

                // 触发浏览器下载
                pdf.save(`${this.candidateName}_${this.currentTicket.name}_准考证.pdf`);
                
                this.$message.success('准考证下载成功');
            } catch (error) {
                console.error("生成PDF出现错误：", error);
                this.$message.error('生成准考证失败，请确保已安装相关依赖。');
            } finally {
                // 关闭 loading 状态
                this.loading = false;
            }
        }
    }
}
</script>

<style scoped>
.ticket-download {
    margin-top: 20px;
}

/* 将用于生成 PDF 的模板移出屏幕可视区域，但保持其在 DOM 树中且处于显示状态以供 html2canvas 读取 */
.ticket-template-container {
    position: fixed;
    top: -9999px;
    left: -9999px;
    z-index: -999;
}

/* 准考证的样式排版 */
.ticket-print-area {
    width: 700px;
    padding: 50px;
    background-color: #ffffff;
    border: 2px solid #000000; /* 外部黑色粗边框 */
    color: #000000;
    font-family: 'SimSun', '宋体', serif; /* 使用标准衬线字体模拟真实纸张 */
}

.ticket-header {
    text-align: center;
    border-bottom: 2px solid #000000;
    padding-bottom: 20px;
    margin-bottom: 40px;
}

.ticket-header h2 {
    margin: 0;
    font-size: 32px;
    letter-spacing: 4px;
}

.ticket-content p {
    font-size: 20px;
    line-height: 2.8;
    margin: 0;
    display: flex;
}

.ticket-content strong {
    display: inline-block;
    width: 140px;
    text-align: right;
    margin-right: 15px;
}

.ticket-footer {
    margin-top: 60px;
    border-top: 1px dashed #000000;
    padding-top: 20px;
    font-size: 16px;
    color: #333333;
    line-height: 1.5;
}
</style>