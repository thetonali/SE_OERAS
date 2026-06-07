<template>
	<div id="exam">
		<div class="exam-toolbar">
			<el-input v-model="key" placeholder="请输入考试名称" prefix-icon="el-icon-search" clearable></el-input>
			<el-button type="primary" @click="searchExam()">搜索考试</el-button>
		</div>

		<div class="section-head">
			<h3>考试中心</h3>
			<span>报名后可在个人中心下载准考证，考试开始后 30 分钟内可进入考试。</span>
		</div>

		<el-row :gutter="20">
			<el-col :span="6" v-for="(item, index) in visibleExams" :key="item.id || index">
				<el-card class="exam-card" :body-style="{ padding: '0px' }" v-loading="loading">
					<img src="@/assets/exam.png" class="image">
					<div class="card-body">
						<h4>{{ item.name }}</h4>
						<p>考试时间：{{ displayExamWindow(item) }}</p>
						<p>考试时长：{{ item.total_time }} 分钟</p>
						<el-tag v-if="isRegistered(item)" type="success" size="small">已报名</el-tag>
						<el-tag v-else type="info" size="small">未报名</el-tag>
						<div class="actions">
							<el-button v-if="!isRegistered(item)" type="primary" size="small" @click="registerExam(item)">
								报名
							</el-button>
							<el-button v-else-if="canEnterExam(item)" type="success" size="small" @click="enterExam(item)">
								进入考试
							</el-button>
							<el-tooltip v-else :content="enterHint(item)" placement="top">
								<el-button type="info" size="small" disabled>等待开考</el-button>
							</el-tooltip>
							<el-button v-if="isRegistered(item)" type="text" size="small" @click="$router.push('/center')">
								下载准考证
							</el-button>
						</div>
					</div>
				</el-card>
			</el-col>
		</el-row>
		<Pagination :count="pagination.count" @size-change="handleSizeChange" @current-change="handleCurrentChange"></Pagination>
	</div>
</template>

<script>
	import Pagination from '@/components/Pagination.vue'
	export default {
		data() {
			return {
				loading: false,
				key: null,
				page: 1,
				page_size: 5,
				registrations: [],
				pagination: {
					count: null,
					next: null,
					previous: null,
					results: []
				}
			}
		},
		components: {
			Pagination
		},
		computed: {
			visibleExams() {
				return (this.pagination.results || []).filter(item => {
					if (this.hasExamEnded(item)) return false
					if (this.isRegistered(item)) return true
					return !this.hasExamStarted(item)
				})
			}
		},
		methods: {
			getExamInfo() {
				this.$axios(`/api/exams/?format=json`, {
					params: {
						page: this.page,
						page_size: this.page_size,
						student_id: this.$store.state.student.id,
					}
				}).then(res => {
					this.pagination = res.data
					this.loading = false
				}).catch(error => {
					console.log(error)
				})
			},
			getRegistrations() {
				this.$axios('/api/registrations/', {
					params: {
						student_id: this.$store.state.student.id,
						page_size: 10
					}
				}).then(res => {
					this.registrations = res.data.results || res.data
				}).catch(error => {
					console.log(error)
				})
			},
			isRegistered(exam) {
				return this.registrations.some(item => item.exam && item.exam.id === exam.id)
			},
			getRegistration(exam) {
				return this.registrations.find(item => item.exam && item.exam.id === exam.id)
			},
			normalizeTime(value, fallback) {
				return (value || fallback).substring(0, 5)
			},
			displayExamWindow(exam) {
				return `${exam.exam_date} ${this.normalizeTime(exam.start_time, '09:00')} - ${this.normalizeTime(exam.end_time, '11:00')}`
			},
			examStartDate(exam) {
				const startTime = this.normalizeTime(exam.start_time, '09:00')
				return new Date(`${exam.exam_date}T${startTime}:00`)
			},
			examEndDate(exam) {
				const start = this.examStartDate(exam)
				if (exam.end_time) {
					const endTime = this.normalizeTime(exam.end_time, '11:00')
					const end = new Date(`${exam.exam_date}T${endTime}:00`)
					if (end <= start) end.setDate(end.getDate() + 1)
					return end
				}
				return new Date(start.getTime() + (exam.total_time || 0) * 60 * 1000)
			},
			hasExamStarted(exam) {
				return Date.now() >= this.examStartDate(exam).getTime()
			},
			hasExamEnded(exam) {
				return Date.now() > this.examEndDate(exam).getTime()
			},
			canEnterExam(exam) {
				const start = this.examStartDate(exam).getTime()
				const close = start + 30 * 60 * 1000
				const now = Date.now()
				return now >= start && now <= close && now <= this.examEndDate(exam).getTime()
			},
			enterHint(exam) {
				const start = this.examStartDate(exam)
				const close = new Date(start.getTime() + 30 * 60 * 1000)
				if (Date.now() < start.getTime()) {
					return `考试入口将在 ${start.toLocaleString()} 开放`
				}
				return `考试开始 30 分钟后不可进入，入口已于 ${close.toLocaleString()} 关闭`
			},
			handleSizeChange(val) {
				this.page_size = val
				this.searchExam()
			},
			handleCurrentChange(val) {
				this.page = val
				this.searchExam()
			},
			searchExam() {
				if (this.key) {
					this.$axios(`/api/exams/?format=json`, {
						params: {
							page: this.page,
							page_size: this.page_size,
							search: this.key,
							student_id: this.$store.state.student.id,
						}
					}).then(res => {
						if (res.status == 200) {
							this.pagination = res.data
						}
					})
				} else {
					this.getExamInfo()
				}
			},
			registerExam(item) {
				if (this.hasExamStarted(item)) {
					this.$message.warning('考试已经开始，不能再报名')
					return
				}
				this.$confirm('确认报名该考试吗？报名成功后可在个人中心下载准考证。', '确认报名', {
					confirmButtonText: '确认',
					cancelButtonText: '取消',
					type: 'warning'
				}).then(() => {
					return this.$axios.post('/api/registrations/', {
						exam_id: item.id,
						student_id: this.$store.state.student.id
					})
				}).then(res => {
					if (!this.registrations.some(reg => reg.id === res.data.id)) {
						this.registrations.unshift(res.data)
					}
					localStorage.setItem("latestRegistration", JSON.stringify(res.data))
					this.$message.success('报名成功，请到个人中心下载准考证')
				}).catch(error => {
					if (error !== 'cancel') {
						console.log(error)
						const detail = error.response && (error.response.status === 500 || error.response.status === 503) ? '请先在后端执行 python manage.py migrate。' : ''
						this.$message.error(`报名失败。${detail}`)
					}
				})
			},
			enterExam(item) {
				const registration = this.getRegistration(item)
				if (!registration) {
					this.$message.error('请先报名该考试')
					return
				}
				localStorage.removeItem('exam')
				localStorage.removeItem('paper')
				sessionStorage.removeItem('isPractice')
				localStorage.setItem("exam", JSON.stringify(item))
				localStorage.setItem("paper", JSON.stringify(item.paper))
				localStorage.setItem("registration", JSON.stringify(registration))
				sessionStorage.setItem("examEntryGranted", `${item.id}`)
				this.$store.commit("setIsPractice", false)
				this.$router.push('/answer')
			}
		},
		created() {
			this.getExamInfo()
			this.getRegistrations()
			this.loading = true
		}
	}
</script>

<style lang="scss" scoped>
	.exam-toolbar {
		display: flex;
		justify-content: center;
		gap: 12px;
		margin-bottom: 22px;
	}

	.exam-toolbar .el-input {
		width: 280px;
	}

	.section-head {
		display: flex;
		align-items: baseline;
		gap: 16px;
		margin-bottom: 16px;
	}

	.section-head h3 {
		border-left: solid 10px rgb(220, 208, 65);
		padding-left: 10px;
		margin: 0;
	}

	.section-head span {
		color: #606266;
	}

	.exam-card {
		margin-bottom: 20px;
		border-radius: 6px;
	}

	.card-body {
		padding: 14px;
	}

	.card-body h4 {
		margin: 0 0 10px 0;
		color: #1f2d3d;
	}

	.card-body p {
		margin: 6px 0;
		color: #606266;
	}

	.actions {
		margin-top: 14px;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.image {
		width: 50%;
		height: 80%;
		display: block;
		margin: 20px auto 10px auto;
	}
</style>
