<template>
	<div id="admit-card">
		<div class="toolbar no-print">
			<el-button type="primary" icon="el-icon-printer" @click="downloadPdf">下载PDF</el-button>
			<el-button icon="el-icon-back" @click="$router.push('/center')">返回个人中心</el-button>
		</div>

		<article class="ticket" id="ticket">
			<header class="ticket-header">
				<div class="system-name">OERAS 在线考试报名与管理系统</div>
				<h1>准考证</h1>
				<div class="ticket-no">准考证号：{{ registration.admission_number }}</div>
			</header>

			<section class="main-info">
				<table>
					<tbody>
						<tr>
							<th>姓名</th>
							<td>{{ student.name }}</td>
							<th>学号</th>
							<td>{{ user.username }}</td>
						</tr>
						<tr>
							<th>性别</th>
							<td>{{ student.gender === 'f' ? '女' : '男' }}</td>
							<th>班级</th>
							<td>{{ clazzName }}</td>
						</tr>
						<tr>
							<th>考试名称</th>
							<td colspan="3">{{ exam.name }}</td>
						</tr>
						<tr>
							<th>考试科目</th>
							<td>{{ paper.subject || exam.major || '通用' }}</td>
							<th>考试日期</th>
							<td>{{ exam.exam_date }}</td>
						</tr>
						<tr>
							<th>开始时间</th>
							<td>{{ (exam.start_time || '09:00').substring(0, 5) }}</td>
							<th>结束时间</th>
							<td>{{ (exam.end_time || '11:00').substring(0, 5) }}</td>
						</tr>
						<tr>
							<th>考试时长</th>
							<td colspan="3">{{ exam.total_time }} 分钟</td>
						</tr>
					</tbody>
				</table>
				<div class="photo">
					<img v-if="avatarUrl" :src="avatarUrl" alt="avatar">
					<div v-else>考生照片</div>
				</div>
			</section>

			<section class="notice">
				<h2>考生须知</h2>
				<ol>
					<li>请考生提前核对个人信息与考试信息，若有错误请及时联系管理员。</li>
					<li>考试入口将于开考前 15 分钟开放，请合理安排时间。</li>
					<li>考试过程中请遵守考试纪律，不得替考、代考或切换身份。</li>
					<li>{{ exam.tips || '请保持网络稳定，按系统提示完成答题与交卷。' }}</li>
				</ol>
			</section>

			<footer class="ticket-footer">
				<span>打印时间：{{ printTime }}</span>
				<span>本准考证由系统自动生成</span>
			</footer>
		</article>
	</div>
</template>

<script>
export default {
	data() {
		return {
			clazz: {},
			printTime: new Date().toLocaleString()
		}
	},
	computed: {
		registration() {
			return localStorage.getItem('registration') ? JSON.parse(localStorage.getItem('registration')) : {}
		},
		exam() {
			return localStorage.getItem('exam') ? JSON.parse(localStorage.getItem('exam')) : {}
		},
		paper() {
			return localStorage.getItem('paper') ? JSON.parse(localStorage.getItem('paper')) : {}
		},
		student() {
			return this.$store.state.student || {}
		},
		user() {
			return this.$store.state.user || {}
		},
		avatarUrl() {
			return this.student.avatar || localStorage.getItem('studentAvatar') || ''
		},
		clazzName() {
			if (!this.clazz.id) return ''
			return `${this.clazz.year}${this.clazz.major}${this.clazz.clazz}`
		}
	},
	methods: {
		getClazzInfo() {
			if (!this.student.clazz) return
			this.$axios(`/api/clazzs/${this.student.clazz}/?format=json`).then(res => {
				this.clazz = res.data
			})
		},
		downloadPdf() {
			this.printTime = new Date().toLocaleString()
			this.$nextTick(() => window.print())
		}
	},
	created() {
		if (!this.registration.id || !this.exam.id) {
			this.$message.warning('请先在个人中心选择已报名考试')
			this.$router.push('/center')
			return
		}
		this.getClazzInfo()
	}
}
</script>

<style lang="scss" scoped>
#admit-card {
	padding: 24px 0 40px 0;
	background: #f5f7fb;
	min-height: calc(100vh - 120px);
}

.toolbar {
	width: 210mm;
	margin: 0 auto 18px auto;
	text-align: right;
}

.ticket {
	width: 190mm;
	min-height: 260mm;
	margin: 0 auto;
	padding: 18mm 14mm;
	box-sizing: border-box;
	background: #ffffff;
	color: #1f2d3d;
	border: 1px solid #dcdfe6;
	box-shadow: 0 12px 36px rgba(31, 45, 61, 0.12);
}

.ticket-header {
	text-align: center;
	border-bottom: 3px solid #1a3a6e;
	padding-bottom: 16px;
	margin-bottom: 22px;
}

.system-name {
	color: #5f7390;
	font-size: 14px;
	letter-spacing: 2px;
}

.ticket-header h1 {
	font-size: 34px;
	margin: 10px 0;
	letter-spacing: 10px;
	color: #1a3a6e;
}

.ticket-no {
	display: inline-block;
	padding: 7px 18px;
	background: #eef5ff;
	border: 1px solid #c6dafc;
	color: #1a3a6e;
	font-weight: 700;
}

.main-info {
	display: grid;
	grid-template-columns: 1fr 35mm;
	gap: 18px;
	align-items: start;
}

table {
	width: 100%;
	border-collapse: collapse;
	font-size: 15px;
}

th,
td {
	border: 1px solid #303133;
	padding: 10px 11px;
	line-height: 1.5;
}

th {
	width: 86px;
	background: #f3f6fb;
	text-align: center;
	font-weight: 700;
}

.photo {
	width: 35mm;
	height: 45mm;
	border: 1px solid #303133;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #909399;
	background: #fafafa;
}

.photo img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.notice {
	margin-top: 28px;
	border: 1px solid #dcdfe6;
	padding: 16px 20px;
	background: #fbfcff;
}

.notice h2 {
	margin: 0 0 10px 0;
	color: #1a3a6e;
	font-size: 18px;
}

.notice ol {
	margin: 0;
	padding-left: 22px;
	line-height: 1.9;
}

.ticket-footer {
	display: flex;
	justify-content: space-between;
	margin-top: 28px;
	padding-top: 12px;
	border-top: 1px dashed #b8c0cc;
	color: #606266;
	font-size: 13px;
}

@media print {
	@page {
		size: A4;
		margin: 10mm;
	}

	body {
		background: #ffffff;
	}

	.no-print,
	.toolbar {
		display: none !important;
	}

	#admit-card {
		padding: 0;
		background: #ffffff;
		min-height: auto;
	}

	.ticket {
		width: 190mm;
		min-height: 267mm;
		margin: 0;
		padding: 12mm;
		border: 1px solid #000000;
		box-shadow: none;
		page-break-inside: avoid;
	}
}
</style>
