from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import TextField, DateTimeField
from django.utils import timezone
from timezone_field import TimeZoneField

from foodsaving.base.base_models import BaseModel, LocationModel
from foodsaving.conversations.models import ConversationMixin
from foodsaving.history.models import History, HistoryTypus
from foodsaving.groups.roles import APPROVED


class GroupManager(models.Manager):
    @transaction.atomic
    def send_all_notifications(self):
        for g in self.all():
            g.send_notifications()


class Group(BaseModel, LocationModel, ConversationMixin):
    objects = GroupManager()

    name = models.CharField(max_length=settings.NAME_MAX_LENGTH, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='groups', through='GroupMembership')
    password = models.CharField(max_length=255, blank=True)
    public_description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    sent_summary_up_to = DateTimeField(null=True)
    timezone = TimeZoneField(default='Europe/Berlin', null=True, blank=True)
    slack_webhook = models.CharField(max_length=255, blank=True)
    active_agreement = models.OneToOneField(
        'groups.Agreement',
        related_name='active_group',
        null=True,
        on_delete=models.SET_NULL
    )

    def approved_member_count(self):
        return self.members_with_all_roles([APPROVED]).count()

    def members_with_all_roles(self, roles):
        return self.members.filter(groupmembership__roles__contains=roles)

    def __str__(self):
        return 'Group {}'.format(self.name)

    def send_notifications(self):
        if self.slack_webhook.startswith('https://hooks.slack.com/services/'):
            for s in self.store.all():
                # get all pick-ups within the notification range
                for p in s.pickup_dates.filter(
                    date__lt=timezone.now() + relativedelta(hours=s.upcoming_notification_hours),
                    date__gt=timezone.now()
                ):
                    p.notify_upcoming_via_slack()

    def add_applicant(self, user):
        """Adds a person to the group marked as being an applicant"""
        GroupMembership.objects.create(group=self, user=user)
        self.create = History.objects.create(typus=HistoryTypus.GROUP_APPLY, group=self, users=[user, ], )

    def add_member(self, user, history_payload=None):
        """Adds a "full" member to the group, e.g. grants the status of a normal member."""
        GroupMembership.objects.create(group=self, user=user, roles=[APPROVED])
        History.objects.create(
            typus=HistoryTypus.GROUP_JOIN,
            group=self,
            users=[user, ],
            payload=history_payload
        )

    def remove_member(self, user):
        if self.is_member(user):
            History.objects.create(
                typus=HistoryTypus.GROUP_LEAVE,
                group=self,
                users=[user, ]
            )
        GroupMembership.objects.filter(group=self, user=user).delete()

    def is_member(self, user):
        return self.is_member_with_role(user, [APPROVED])

    def is_member_with_role(self, user, role_name):
        return not user.is_anonymous and GroupMembership.objects.filter(group=self, user=user,
                                                                        roles__contains=[role_name]).exists()

    def accept_invite(self, user, invited_by, invited_at):
        self.add_member(user, history_payload={
            'invited_by': invited_by.id,
            'invited_at': invited_at.isoformat(),
            'invited_via': 'e-mail'
        })

    def members_with_notification_type(self, type):
        return self.members.filter(groupmembership__notification_types__contains=[type])


class Agreement(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = TextField()
    content = TextField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='agreements', through='UserAgreement')


class UserAgreement(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)


class GroupNotificationType(object):
    WEEKLY_SUMMARY = 'weekly_summary'


def get_default_notification_types():
    return [GroupNotificationType.WEEKLY_SUMMARY]


class GroupMembershipManager(models.Manager):
    pass


class GroupMembership(BaseModel):
    objects = GroupMembershipManager()

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roles = ArrayField(TextField(), default=list)
    lastseen_at = DateTimeField(default=timezone.now)
    notification_types = ArrayField(TextField(), default=get_default_notification_types)

    class Meta:
        db_table = 'groups_group_members'
        unique_together = (('group', 'user'),)

    def add_roles(self, roles):
        for role in roles:
            if role not in self.roles:
                self.roles.append(role)
                if role is APPROVED:
                    History.objects.create(
                        typus=HistoryTypus.GROUP_JOIN,
                        group=self.group,
                        users=[self.user, ],
                    )

    def remove_roles(self, roles):
        for role in roles:
            while role in self.roles:
                self.roles.remove(role)

    def add_notification_types(self, notification_types):
        for notification_type in notification_types:
            if notification_type not in self.notification_types:
                self.notification_types.append(notification_type)

    def remove_notification_types(self, notification_types):
        for notification_type in notification_types:
            while notification_type in self.notification_types:
                self.notification_types.remove(notification_type)
