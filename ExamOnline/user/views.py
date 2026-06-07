from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.utils import OperationalError
from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import Student, Clazz, Teacher, StudentProfile
from user.serializers import StudentSerializer, UserDetailSerializer, ClazzSerializer


class CustomBackend(ModelBackend):
    """自定义用户验证"""

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # ===== 去掉 Q(mobile=username)，User 模型没有 mobile 字段会报错 =====
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except Exception:
            return None


def jwt_response_payload_handler(token, user=None, request=None):
    """
    设置 jwt 登录后返回的数据
    ===== 核心修改：根据用户类型返回不同数据，教师/管理员不再崩溃 =====
    """
    # 判断是否是超级管理员
    if user.is_superuser:
        return {
            'token': token,
            'role': 'admin',
            'user': UserDetailSerializer(user, context={'request': request}).data,
            'student': None,
        }

    # 判断是否是教师
    try:
        teacher = Teacher.objects.get(user=user)
        return {
            'token': token,
            'role': 'teacher',
            'user': UserDetailSerializer(user, context={'request': request}).data,
            'student': None,
            'teacher_name': teacher.name,
        }
    except Teacher.DoesNotExist:
        pass

    # 普通学生
    try:
        student = Student.objects.get(user=user)
        return {
            'token': token,
            'role': 'student',
            'user': UserDetailSerializer(user, context={'request': request}).data,
            'student': StudentSerializer(student, context={'request': request}).data,
        }
    except Student.DoesNotExist:
        # 兜底：有 User 但没有 Student 也没有 Teacher（异常情况）
        return {
            'token': token,
            'role': 'unknown',
            'user': UserDetailSerializer(user, context={'request': request}).data,
            'student': None,
        }


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """用户注册"""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        if User.objects.filter(username=username).exists():
            return Response({'msg': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

        user_detail = UserDetailSerializer(data=request.data)
        if user_detail.is_valid():
            user_detail.save()
            user = User.objects.get(username=username)
            user.password = make_password(user.password)
            user.save()

            name = request.data.get('name', username)
            student = Student(user=user, name=name)
            student.save()
            return Response({'msg': '注册成功'}, status=status.HTTP_201_CREATED)

        return Response(user_detail.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePwdApi(APIView):
    """修改用户密码"""

    def patch(self, request):
        old_pwd = request.data['oldpwd']
        new_pwd = request.data['newpwd']
        user_id = request.data['userid']
        user = User.objects.get(id=user_id)
        if user.check_password(old_pwd):
            user.set_password(new_pwd)
            user.save()
            return Response(data={'msg': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'msg': 'fail'}, status=status.HTTP_200_OK)


class StudentViewSet(viewsets.ModelViewSet):
    """学生信息"""
    queryset = Student.objects.all().order_by('id')
    serializer_class = StudentSerializer

    def update(self, request, *args, **kwargs):
        avatar = request.data.get('avatar')
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK and avatar is not None:
            try:
                StudentProfile.objects.update_or_create(
                    student=self.get_object(),
                    defaults={'avatar': avatar}
                )
                response.data['avatar'] = avatar
            except OperationalError:
                response.data['avatar_error'] = '学生扩展资料表尚未创建，请先执行 python manage.py migrate'
        return response


class ClazzListViewSet(viewsets.ModelViewSet):
    """班级信息"""
    queryset = Clazz.objects.all().order_by('id')
    serializer_class = ClazzSerializer
