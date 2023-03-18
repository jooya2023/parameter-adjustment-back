from accounts.models import User, UserType

from django.contrib.auth.models import Group


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
            Group.objects.create(
                name="SysAdmin"
            )
            return True
        return False

    def create_group_for_supervisor(self):
        check_exists_group = Group.objects.filter(name="Supervisor").exists()

        if not check_exists_group:
            Group.objects.create(
                name="Supervisor"
            )
            return True
        return False

    def create_group_for_operation(self):
        check_exists_group = Group.objects.filter(name="Operation").exists()

        if not check_exists_group:
            Group.objects.create(
                name="Operation"
            )
            return True
        return False

    def create_group_for_monitoring(self):
        check_exists_group = Group.objects.filter(name="Monitoring").exists()

        if not check_exists_group:
            Group.objects.create(
                name="Monitoring"
            )
            return True
        return False

    def create_user_type_sysadmin(self):
        check_exists_user_type = UserType.objects.filter(name="SysAdmin")

        if not check_exists_user_type:
            UserType.objects.create(
                name="SysAdmin"
            )
            return True
        return False

    def create_user_type_supervisor(self):
        check_exists_user_type = UserType.objects.filter(name="Supervisor")

        if not check_exists_user_type:
            UserType.objects.create(
                name="Supervisor"
            )
            return True
        return False

    def create_user_type_operation(self):
        check_exists_user_type = UserType.objects.filter(name="Operation")

        if not check_exists_user_type:
            UserType.objects.create(
                name="Operation"
            )
            return True
        return False

    def create_user_type_monitoring(self):
        check_exists_user_type = UserType.objects.filter(name="Monitoring")

        if not check_exists_user_type:
            UserType.objects.create(
                name="Monitoring"
            )
            return True
        return False

