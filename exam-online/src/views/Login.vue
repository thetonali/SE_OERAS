<template>
  <div class="login-container">
    <!-- 左侧装饰区 -->
    <div class="login-left">
      <div class="left-content">
        <div class="system-logo">
          <span class="logo-icon">📋</span>
        </div>
        <h1 class="system-title">在线考试报名与<br />考试管理系统</h1>
        <p class="system-subtitle">
          Online Examination Registration<br />
          and Administration System
        </p>
        <p class="system-abbr">OERAS</p>
        <div class="system-desc">
          <p>· 便捷在线报名，安全缴费认证</p>
          <p>· 公平在线考试，科学智能评分</p>
          <p>· 透明成绩查询，高效管理运营</p>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单区 -->
    <div class="login-right">
      <div class="login-card">
        <h2 class="card-title">用户登录</h2>
        <p class="card-sub">欢迎使用 OERAS 在线考试管理系统</p>

        <el-form
          :model="loginForm"
          :rules="loginRules"
          ref="loginFormRef"
          label-position="top"
        >
          <el-form-item label="账号（用户名）" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="el-icon-user"
              clearable
            ></el-input>
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="el-icon-lock"
              show-password
              clearable
            ></el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <span>还没有账号？</span>
          <el-button type="text" @click="goRegister">立即注册</el-button>
        </div>

        <div class="login-tip">
          <el-alert
            title="系统提示：本系统面向考生、教师及管理员开放，登录后将根据账号类型自动跳转至对应功能界面。"
            type="info"
            :closable="false"
            show-icon
          ></el-alert>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      loading: false,
      loginForm: {
        username: "",
        password: ""
      },
      loginRules: {
        username: [
          { required: true, message: "请输入学号", trigger: "blur" }
        ],
        password: [
          { required: true, message: "请输入密码", trigger: "blur" }
        ]
      }
    };
  },

  methods: {
    handleLogin() {
      localStorage.clear();
      sessionStorage.clear();

      this.$refs.loginFormRef.validate(valid => {
        if (!valid) return;

        this.loading = true;

        const msg = this;

        // ===== 使用原有登录接口和逻辑 =====
        axios
          .post("api/jwt-auth/", this.loginForm)
          .then(res => {
            this.loading = false;

            if (res.status === 200) {
              this.$message({
                message: "登录成功",
                type: "success"
              });

              this.$store.commit("setUser", res.data.user);
              this.$store.commit("setStudent", res.data.student);
              this.$store.commit("setAuthorization", res.data.token);

              this.$router.push("/exam");
            }
          })
          .catch(function(error) {
            msg.loading = false;
            msg.$message.error("登录失败，账号或密码错误");
            console.log(error);
          });
      });
    },

    goRegister() {
      this.$router.push("/register");
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-image: none;
  font-family: "SimSun", "宋体", "STSong", serif;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1a3a6e 0%, #2563eb 60%, #1e90ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.left-content {
  color: #ffffff;
  text-align: center;
}

.logo-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.system-title {
  font-size: 32px;
  font-weight: bold;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.system-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 8px 0;
  line-height: 1.6;
}

.system-abbr {
  font-size: 28px;
  font-weight: bold;
  letter-spacing: 6px;
  margin: 12px 0 24px 0;
}

.system-desc {
  text-align: left;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 16px 20px;
  margin-top: 16px;
}

.system-desc p {
  margin: 6px 0;
  font-size: 14px;
}

.login-right {
  width: 480px;
  background-color: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  width: 100%;
  background: #ffffff;
  border-radius: 12px;
  padding: 40px 36px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 24px;
  font-weight: bold;
  color: #1a3a6e;
  margin: 0 0 8px 0;
}

.card-sub {
  font-size: 13px;
  color: #888888;
  margin: 0 0 28px 0;
}

.el-form-item {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(90deg, #1a3a6e, #2563eb);
  border: none;
  border-radius: 6px;
  letter-spacing: 4px;
}

.login-btn:hover {
  background: linear-gradient(90deg, #2563eb, #1a3a6e);
}

.login-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #666666;
}

.login-tip {
  margin-top: 20px;
}

.login-tip .el-alert {
  font-size: 12px;
}

@media (max-width: 768px) {
  .login-left {
    display: none;
  }

  .login-right {
    width: 100%;
  }
}
</style>