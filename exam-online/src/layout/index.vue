<template>
	<div id="layout">
		<el-container>
			<el-header height="64px">
				<div class="brand" @click="$router.push('/exam')">
					<img src="../assets/logo.png" height="42px" />
					<span>OERAS 学生端</span>
				</div>
				<el-menu :default-active="activeIndex" class="nav" mode="horizontal" @select="handleSelect"
				 background-color="#ffffff" text-color="#5f7390" active-text-color="#2563eb" :router="true">
					<el-menu-item index="/exam">考试中心</el-menu-item>
					<el-menu-item index="/practice">模拟练习</el-menu-item>
					<el-menu-item index="/grade">成绩查询</el-menu-item>
					<el-menu-item index="/center">个人中心</el-menu-item>
				</el-menu>
				<el-dropdown>
					<span class="el-dropdown-link">
						<i class="el-icon-user-solid"></i>
						<span>{{ getStudent.name || '学生' }}</span>
						<i class="el-icon-arrow-down el-icon--right"></i>
					</span>
					<el-dropdown-menu slot="dropdown">
						<el-dropdown-item>
							<el-button type="text" @click="toCenter">个人中心</el-button>
						</el-dropdown-item>
						<el-dropdown-item>
							<el-button type="text" @click="toUpdatePwd">修改密码</el-button>
						</el-dropdown-item>
						<el-dropdown-item divided>
							<el-button type="text" @click="loginOut">退出登录</el-button>
						</el-dropdown-item>
					</el-dropdown-menu>
				</el-dropdown>
			</el-header>
			<el-main>
				<router-view />
			</el-main>
			<el-footer height="48px">
				<b>@Copyright 2019-2020. ALL Rights Reserved</b>
			</el-footer>
		</el-container>
	</div>
</template>

<script>
	export default {
		name: "layout",
		data() {
			return {
				activeIndex: this.$route.path
			}
		},
		computed: {
			getStudent() {
				return this.$store.state.student
			}
		},
		watch: {
			'$route.path'(value) {
				this.activeIndex = value
			}
		},
		methods: {
			handleSelect(key) {
				this.activeIndex = key
			},
			loginOut() {
				localStorage.clear()
				sessionStorage.clear()
				this.$router.push('/login')
			},
			toCenter() {
				this.$router.push({ name: 'Center' })
			},
			toUpdatePwd() {
				this.$router.push({ name: 'Password' })
			}
		}
	}
</script>

<style lang="scss" scoped>
	#layout {
		min-height: 100vh;
		background: #f5f7fb;
	}

	.el-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 40px;
		background: #ffffff;
		border-bottom: solid 1px #e6eaf0;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 10px;
		cursor: pointer;
		font-size: 18px;
		font-weight: 700;
		color: #1a3a6e;
	}

	.nav {
		border-bottom: none;
		flex: 1;
		margin-left: 40px;
	}

	.el-main {
		width: 1180px;
		min-height: calc(100vh - 112px);
		margin: 0 auto;
		padding: 24px 0;
	}

	.el-footer {
		text-align: center;
		color: #8c9aae;
		line-height: 48px;
	}

	.el-dropdown-link {
		cursor: pointer;
		color: #5f7390;
		font-size: 16px;
	}
</style>
