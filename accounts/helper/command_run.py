from accounts.models import User, UserType

from django.contrib.auth.models import Group, Permission


class CommandAccounts(object):
    def create_god_user(self):
        check_exists_user = User.objects.filter(username="poshtiban").exists()

        if not check_exists_user:
            User.objects.create_user(
                username="poshtiban",
                password="@poshtiban",
                first_name="پشتیبان",
                last_name="سیستم",
                is_superuser=True,
                is_staff=True,
            )
            return True
        return False

    def create_group_for_sysadmin(self):
        check_exists_group = Group.objects.filter(name="SysAdmin").exists()

        if not check_exists_group:
            group = Group.objects.create(
                name="SysAdmin"
            )
            lst_perm = []
            permissions = Permission.objects.all()
            for permission in permissions:
                lst_perm.append(permission)
            group.permissions.set(lst_perm)
            return True
        return False

    def create_group_for_supervisor(self):
        check_exists_group = Group.objects.filter(name="Supervisor").exists()

        if not check_exists_group:
            group = Group.objects.create(
                name="Supervisor"
            )
            lst_perm = []
            permissions = Permission.objects.all()
            for permission in permissions:
                lst_perm.append(permission)
            group.permissions.set(lst_perm)
            return True
        return False

    def create_group_for_operation(self):
        check_exists_group = Group.objects.filter(name="Operation").exists()

        if not check_exists_group:
            group = Group.objects.create(
                name="Operation"
            )
            lst_perm = []
            permissions = Permission.objects.all()
            for permission in permissions:
                lst_perm.append(permission)
            group.permissions.set(lst_perm)
            return True
        return False

    def create_group_for_monitoring(self):
        check_exists_group = Group.objects.filter(name="Monitoring").exists()

        if not check_exists_group:
            group = Group.objects.create(
                name="Monitoring"
            )
            lst_perm = []
            permissions = Permission.objects.all()
            for permission in permissions:
                lst_perm.append(permission)
            group.permissions.set(lst_perm)
            return True
        return False

    def create_user_type_sysadmin(self):
        check_exists_user_type = UserType.objects.filter(name="SysAdmin").exists()

        if not check_exists_user_type:
            UserType.objects.create(
                name="SysAdmin"
            )
            return True
        return False

    def create_user_type_supervisor(self):
        check_exists_user_type = UserType.objects.filter(name="Supervisor").exists()

        if not check_exists_user_type:
            UserType.objects.create(
                name="Supervisor"
            )
            return True
        return False

    def create_user_type_operation(self):
        check_exists_user_type = UserType.objects.filter(name="Operation").exists()

        if not check_exists_user_type:
            UserType.objects.create(
                name="Operation"
            )
            return True
        return False

    def create_user_type_monitoring(self):
        check_exists_user_type = UserType.objects.filter(name="Monitoring").exists()

        if not check_exists_user_type:
            UserType.objects.create(
                name="Monitoring"
            )
            return True
        return False

    def create_user_sysadmin(self):
        check_exists_user = User.objects.filter(username="sysadmin").exists()

        if not check_exists_user:
            user_type = UserType.objects.get(name="SysAdmin")
            user = User.objects.create_user(
                user_type=user_type,
                username="sysadmin",
                password="1234",
                first_name="مدیر",
                last_name="سیستم",
                is_staff=True
            )
            group = Group.objects.get(name="SysAdmin")
            group.user_set.add(user)
            return True
        return False

    def create_user_supervisor(self):
        check_exists_user = User.objects.filter(username="supervisor").exists()

        if not check_exists_user:
            user_type = UserType.objects.get(name="Supervisor")
            user = User.objects.create_user(
                user_type=user_type,
                username="supervisor",
                password="1234",
                first_name="سرپرست",
                last_name="سیستم",
                is_staff=True
            )
            group = Group.objects.get(name="Supervisor")
            group.user_set.add(user)
            return True
        return False

    def create_user_operation(self):
        check_exists_user = User.objects.filter(username="operation").exists()

        if not check_exists_user:
            user_type = UserType.objects.get(name="Operation")
            user = User.objects.create_user(
                user_type=user_type,
                username="operation",
                password="1234",
                first_name="اپراتور",
                last_name="سیستم",
                is_staff=True
            )
            group = Group.objects.get(name="Operation")
            group.user_set.add(user)
            return True
        return False

    def create_user_monitoring(self):
        check_exists_user = User.objects.filter(username="monitoring").exists()

        if not check_exists_user:
            user_type = UserType.objects.get(name="Monitoring")
            user = User.objects.create_user(
                user_type=user_type,
                username="monitoring",
                password="1234",
                first_name="نظارت کننده",
                last_name="سیستم",
                is_staff=True
            )
            group = Group.objects.get(name="Monitoring")
            group.user_set.add(user)
            return True
        return False
