<template>
	<div class="register-page">
		<section class="brand-panel">
			<div>
				<div class="brand-mark">OERAS</div>
				<h1>在线考试报名与管理系统</h1>
				<p>完成账号注册后，可在线报名考试、参加答题、查询成绩并下载准考证。</p>
			</div>
		</section>

		<section class="form-panel">
			<div class="register-card">
				<h2>创建学生账号</h2>
				<p class="sub">请填写真实学号和姓名，便于后台核验考试名单。</p>
				<el-form ref="registerForm" status-icon :model="registerForm" :rules="rules" label-position="top">
					<el-form-item label="学号" prop="username">
						<el-input v-model="registerForm.username" prefix-icon="el-icon-user" autocomplete="off"></el-input>
					</el-form-item>
					<el-form-item label="姓名" prop="name">
						<el-input v-model="registerForm.name" prefix-icon="el-icon-edit" autocomplete="off"></el-input>
					</el-form-item>
					<el-form-item label="密码" prop="password">
						<el-input type="password" v-model="registerForm.password" prefix-icon="el-icon-lock" show-password autocomplete="off"></el-input>
					</el-form-item>
					<el-form-item label="确认密码" prop="checkpwd">
						<el-input type="password" v-model="registerForm.checkpwd" prefix-icon="el-icon-lock" show-password autocomplete="off"></el-input>
					</el-form-item>
					<slide-verification @check-result="checkResult"></slide-verification>
					<el-button type="primary" class="submit-btn" :loading="loading" @click.native.prevent="handRegister('registerForm')">
						注册
					</el-button>
					<div class="text-foot">
						已有账号？
						<router-link to="/login" class="login-link">返回登录</router-link>
					</div>
				</el-form>
			</div>
		</section>
	</div>
</template>

<script>
	import SlideVerification from '@/components/SlideVerification.vue'
	export default {
		data() {
			var validatePass = (rule, value, callback) => {
				if (value === '') {
					callback(new Error('请输入密码'))
				} else {
					if (this.registerForm.checkpwd !== '') {
						this.$refs.registerForm.validateField('checkpwd')
					}
					callback()
				}
			}
			var validatePass2 = (rule, value, callback) => {
				if (value === '') {
					callback(new Error('请再次输入密码'))
				} else if (value !== this.registerForm.password) {
					callback(new Error('两次输入密码不一致'))
				} else {
					callback()
				}
			}
			return {
				confirmSuccess: false,
				loading: false,
				registerForm: {
					username: null,
					password: null,
					checkpwd: null,
					name: null,
				},
				rules: {
					username: [
						{ required: true, message: '请输入学号', trigger: 'blur' },
						{ min: 6, max: 15, message: '长度在 6 到 15 个字符', trigger: 'blur' }
					],
					password: [
						{ required: true, message: '请输入密码', trigger: 'blur' },
						{ min: 6, max: 15, message: '长度在 6 到 15 个字符', trigger: 'blur' },
						{ validator: validatePass, trigger: 'blur' }
					],
					checkpwd: [
						{ required: true, message: '请再次输入密码', trigger: 'blur' },
						{ min: 6, max: 15, message: '长度在 6 到 15 个字符', trigger: 'blur' },
						{ validator: validatePass2, trigger: 'blur' }
					],
					name: [
						{ required: true, message: '请输入姓名', trigger: 'blur' },
						{ min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur' }
					]
				}
			}
		},
		components: {
			SlideVerification
		},
		methods: {
			checkResult(message) {
				this.confirmSuccess = message
			},
			handRegister(formName) {
				if (!this.confirmSuccess) {
					this.$message('请拖动滑块进行验证')
					return
				}
				this.$refs[formName].validate((valid) => {
					if (!valid) return
					this.loading = true
					axios.post(`api/register/`, this.registerForm).then(res => {
						this.loading = false
						if (res.status === 200 || res.status === 201) {
							this.$message.success('注册成功')
							this.$router.push('/login')
						} else {
							this.$message.error(res.data.msg || '注册失败')
						}
					}).catch(error => {
						this.loading = false
						const msg = error.response && error.response.data && error.response.data.msg
						this.$message.error(msg || '注册失败')
						console.log(error)
					})
				})
			}
		}
	}
</script>

<style lang="scss" scoped>
	.register-page {
		display: flex;
		min-height: 100vh;
		background: #f0f2f5;
		font-family: "SimSun", "宋体", "STSong", serif;
	}

	.brand-panel {
		flex: 1;
		background:
			linear-gradient(135deg, rgba(26, 58, 110, 0.94), rgba(37, 99, 235, 0.82));
		color: #ffffff;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 56px;
	}

	.brand-mark {
		font-size: 18px;
		letter-spacing: 8px;
		margin-bottom: 18px;
	}

	.brand-panel h1 {
		font-size: 34px;
		margin: 0 0 16px 0;
	}

	.brand-panel p {
		width: 430px;
		line-height: 1.8;
		font-size: 15px;
	}

	.form-panel {
		width: 500px;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40px;
	}

	.register-card {
		width: 100%;
		background: #ffffff;
		border-radius: 12px;
		padding: 36px;
		box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
	}

	.register-card h2 {
		margin: 0 0 8px 0;
		color: #1a3a6e;
	}

	.sub {
		margin: 0 0 24px 0;
		color: #606266;
		font-size: 13px;
	}

	.submit-btn {
		width: 100%;
		height: 42px;
		margin-top: 18px;
	}

	.text-foot {
		text-align: center;
		margin-top: 18px;
		font-weight: 700;
	}

	.login-link {
		color: #2563eb;
	}
</style>
