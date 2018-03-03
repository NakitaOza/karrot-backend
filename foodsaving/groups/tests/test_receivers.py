from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from foodsaving.conversations.models import Conversation
from foodsaving.groups.factories import GroupFactory
from foodsaving.users.factories import UserFactory


class TestConversationReceiver(TestCase):
    def setUp(self):
        self.invited_by = UserFactory()
        self.group = GroupFactory(members=[self.invited_by, ])
        self.user = UserFactory()
        self.invited_at = timezone.now()

    def test_creates_conversation(self):
        group = GroupFactory()
        conversation = self.get_conversation_for_group(group)
        self.assertIsInstance(conversation, Conversation, 'Did not have a conversation')

    def test_conversation_deleted(self):
        group = GroupFactory()
        conversation_id = group.conversation.id
        group.delete()
        with self.assertRaises(Conversation.DoesNotExist):
            self.assertIsNone(Conversation.objects.get(pk=conversation_id))

    def test_not_adds_participant_not_approved(self):
        group = GroupFactory()
        user = UserFactory()
        group.add_applicant(user)
        conversation = self.get_conversation_for_group(group)
        self.assertNotIn(user, conversation.participants.all(), 'Conversation did have not approved user in')

    def test_adds_participant_when_approved(self):
        group = GroupFactory()
        user = UserFactory()
        group.add_member(user)
        conversation = self.get_conversation_for_group(group)
        self.assertIn(user, conversation.participants.all(), 'Conversation did not have user in')

    def test_removes_participant(self):
        user = UserFactory()
        group = GroupFactory(members=[user])
        group.remove_member(user)
        conversation = self.get_conversation_for_group(group)
        self.assertNotIn(user, conversation.participants.all(), 'Conversation still had user in')

    def get_conversation_for_group(self, group):
        return Conversation.objects.filter(target_id=group.id,
                                           target_type=ContentType.objects.get_for_model(group)).first()
