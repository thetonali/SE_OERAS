<template>
	<div class="center-page">
		<section class="profile-panel">
			<div class="avatar-preview">
				<img v-if="avatarUrl" :src="avatarUrl" alt="avatar">
				<i v-else class="el-icon-user-solid"></i>
			</div>
			<el-form ref="centerForm" status-icon :model="centerForm" :rules="rules" label-width="72px">
				<h1>个人中心</h1>
				<el-form-item label="姓名" prop="name">
					<el-input v-model="centerForm.name"></el-input>
				</el-form-item>
				<el-form-item label="性别" prop="gender">
					<el-select v-model="centerForm.gender" placeholder="请选择性别">
						<el-option label="男" value="m"></el-option>
						<el-option label="女" value="f"></el-option>
					</el-select>
				</el-form-item>
				<el-form-item label="班级" prop="clazz">
					<el-select v-model="centerForm.clazz" placeholder="请选择班级">
						<el-option v-for="item in clazzOptions" :key="item.id" :label="item.year + item.major + item.clazz" :value="item.id">
						</el-option>
					</el-select>
				</el-form-item>
				<el-form-item label="头像">
					<el-input v-model="avatarUrl" placeholder="请输入头像图片地址"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="updateInfo('centerForm')">保存资料</el-button>
					<el-button @click="cancel">返回</el-button>
				</el-form-item>
			</el-form>
		</section>

		<section class="registration-panel">
			<div class="panel-head">
				<h2>已报名考试</h2>
				<el-button icon="el-icon-refresh" circle @click="getRegistrations"></el-button>
			</div>
			<el-table :data="registrations" border style="width: 100%" empty-text="暂无报名记录">
				<el-table-column prop="exam.name" label="考试名称"></el-table-column>
				<el-table-column label="考试时间" width="230">
					<template slot-scope="scope">
						{{ displayExamWindow(scope.row.exam) }}
					</template>
				</el-table-column>
				<el-table-column prop="admission_number" label="准考证号" width="270"></el-table-column>
				<el-table-column prop="create_time" label="报名时间" width="170">
					<template slot-scope="scope">
						{{ scope.row.create_time.replace('T', ' ').substring(0, 19) }}
					</template>
				</el-table-column>
				<el-table-column label="操作" width="130">
					<template slot-scope="scope">
						<el-button type="text" @click="downloadAdmitCard(scope.row)">下载准考证</el-button>
					</template>
				</el-table-column>
			</el-table>
		</section>
	</div>
</template>

<script>
	export default {
		data() {
			return {
				centerForm: {
					name: null,
					gender: null,
					clazz: null,
					clazz_id: null,
					user: null
				},
				avatarUrl: localStorage.getItem('studentAvatar') || '',
				clazzOptions: [],
				registrations: [],
				rules: {
					name: [
						{ required: true, message: '请输入姓名', trigger: 'blur' },
						{ min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur' }
					],
					gender: [
						{ required: true, message: '请选择性别', trigger: 'change' }
					],
					clazz: [
						{ required: true, message: '请选择班级', trigger: 'change' }
					]
				}
			}
		},
		methods: {
			updateInfo(formName) {
				this.$refs[formName].validate((valid) => {
					if (!valid) return
					const payload = Object.assign({}, this.centerForm, {
						clazz_id: this.centerForm.clazz,
						avatar: this.avatarUrl || ''
					})
					this.$axios.patch(
						`/api/students/${this.centerForm.id}/?format=json`,
						payload
					).then(res => {
						if (res.status == 200) {
							localStorage.setItem('studentAvatar', this.avatarUrl || '')
							this.$store.commit("setStudent", res.data)
							this.centerForm = Object.assign({}, res.data)
							this.avatarUrl = res.data.avatar || this.avatarUrl || ''
							this.$message.success('个人信息已更新')
						} else {
							this.$message.error('更新个人信息失败')
						}
					}).catch(error => {
						console.log(error)
						this.$message.error('更新个人信息失败')
					})
				})
			},
			getClazzInfo() {
				this.$axios(`/api/clazzs/?format=json`).then(res => {
					this.clazzOptions = res.data
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
					const latest = localStorage.getItem('latestRegistration') ? JSON.parse(localStorage.getItem('latestRegistration')) : null
					if (latest && latest.id && !this.registrations.some(item => item.id === latest.id)) {
						this.registrations.unshift(latest)
					}
				}).catch(error => {
					console.log(error)
					const detail = error.response && (error.response.status === 500 || error.response.status === 503) ? '请先在后端执行 python manage.py migrate。' : ''
					this.$message.error(`报名记录加载失败。${detail}`)
				})
			},
			downloadAdmitCard(registration) {
				localStorage.setItem("exam", JSON.stringify(registration.exam))
				localStorage.setItem("paper", JSON.stringify(registration.exam.paper))
				localStorage.setItem("registration", JSON.stringify(registration))
				this.$router.push('/admit-card')
			},
			displayExamWindow(exam) {
				if (!exam) return ''
				const start = (exam.start_time || '09:00').substring(0, 5)
				const end = (exam.end_time || '11:00').substring(0, 5)
				return `${exam.exam_date} ${start} - ${end}`
			},
			cancel() {
				this.$router.push('/')
			}
		},
		created() {
			this.centerForm = Object.assign({}, this.$store.state.student)
			this.avatarUrl = this.centerForm.avatar || localStorage.getItem('studentAvatar') || ''
			this.getClazzInfo()
			this.getRegistrations()
		}
	}
</script>

<style lang="scss" scoped>
	.center-page {
		display: grid;
		grid-template-columns: 360px 1fr;
		gap: 24px;
		padding: 24px 0;
	}

	.profile-panel,
	.registration-panel {
		background: #ffffff;
		border: 1px solid #e4e7ed;
		border-radius: 6px;
		padding: 24px;
	}

	.avatar-preview {
		width: 96px;
		height: 96px;
		border-radius: 50%;
		background: #eef5ff;
		margin: 0 auto 18px auto;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
		color: #409eff;
		font-size: 44px;
	}

	.avatar-preview img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	h1,
	h2 {
		margin: 0 0 18px 0;
		color: #1f2d3d;
	}

	.el-select {
		width: 100%;
	}

	.panel-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
</style>
