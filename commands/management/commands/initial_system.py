from django.core.management.base import BaseCommand

from accounts.helper.command_run import CommandAccounts


class Command(BaseCommand):
    help = "initial system"

    def __init__(self):
        super().__init__()
        self.command_accounts = CommandAccounts()

    def handle(self, *args, **options):
        god_user = self.command_accounts.create_god_user()
        if god_user:
            self.stdout.write(self.style.SUCCESS('Success : god user create.'))
        elif not god_user:
            self.stdout.write(self.style.WARNING('Warning : god user exist!'))

        create_group_admin = self.command_accounts.create_group_for_sysadmin()
        if create_group_admin:
            self.stdout.write(self.style.SUCCESS('Success : group for sysadmin create.'))
        elif not create_group_admin:
            self.stdout.write(self.style.WARNING('Warning : group for sysadmin exist!'))

        create_group_supervisor = self.command_accounts.create_group_for_supervisor()
        if create_group_supervisor:
            self.stdout.write(self.style.SUCCESS('Success : group for supervisor create.'))
        elif not create_group_supervisor:
            self.stdout.write(self.style.WARNING('Warning : group for supervisor exist!'))

        create_group_operation = self.command_accounts.create_group_for_operation()
        if create_group_operation:
            self.stdout.write(self.style.SUCCESS('Success : group for operation create.'))
        elif not create_group_operation:
            self.stdout.write(self.style.WARNING('Warning : group for operation exist!'))

        create_group_monitoring = self.command_accounts.create_group_for_monitoring()
        if create_group_monitoring:
            self.stdout.write(self.style.SUCCESS('Success : group for monitoring create.'))
        elif not create_group_monitoring:
            self.stdout.write(self.style.WARNING('Warning : group for monitoring exist!'))

        create_user_type_sysadmin = self.command_accounts.create_user_type_sysadmin()
        if create_user_type_sysadmin:
            self.stdout.write(self.style.SUCCESS('Success : user type sysadmin create.'))
        elif not create_user_type_sysadmin:
            self.stdout.write(self.style.WARNING('Warning : user type sysadmin exist!'))

        create_user_type_supervisor = self.command_accounts.create_user_type_supervisor()
        if create_user_type_supervisor:
            self.stdout.write(self.style.SUCCESS('Success : user type supervisor create.'))
        elif not create_user_type_supervisor:
            self.stdout.write(self.style.WARNING('Warning : user type supervisor exist!'))

        create_user_type_operation = self.command_accounts.create_user_type_operation()
        if create_user_type_operation:
            self.stdout.write(self.style.SUCCESS('Success : user type operation create.'))
        elif not create_user_type_operation:
            self.stdout.write(self.style.WARNING('Warning : user type operation exist!'))

        create_user_type_monitoring = self.command_accounts.create_user_type_monitoring()
        if create_user_type_monitoring:
            self.stdout.write(self.style.SUCCESS('Success : user type monitoring create.'))
        elif not create_user_type_monitoring:
            self.stdout.write(self.style.WARNING('Warning : user type monitoring exist!'))

        create_user_sysadmin = self.command_accounts.create_user_sysadmin()
        if create_user_sysadmin:
            self.stdout.write(self.style.SUCCESS('Success: user sysadmin created.'))
        elif not create_user_sysadmin:
            self.stdout.write(self.style.WARNING('Warning : user sysadmin exists.'))

        create_user_supervisor = self.command_accounts.create_user_supervisor()
        if create_user_supervisor:
            self.stdout.write(self.style.SUCCESS('Success: user supervisor created.'))
        elif not create_user_supervisor:
            self.stdout.write(self.style.WARNING('Warning : user supervisor exists!'))

        create_user_operation = self.command_accounts.create_user_operation()
        if create_user_operation:
            self.stdout.write(self.style.SUCCESS('Success: user operation created.'))
        elif not create_user_operation:
            self.stdout.write(self.style.WARNING('Warning : user operation exists!'))

        create_user_monitoring = self.command_accounts.create_user_monitoring()
        if create_user_monitoring:
            self.stdout.write(self.style.SUCCESS('Success: user monitoring created.'))
        elif not create_user_monitoring:
            self.stdout.write(self.style.WARNING('Warning : user monitoring exists!'))
