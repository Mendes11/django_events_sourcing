import uuid
from datetime import datetime

from django.conf import settings
from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock

from tests.test_app.models import Model1, ModelNoEvent, StatusModel, \
    StatusModel2


class TestModelDispatcher(TestCase):
    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def setUp(self, mock) -> None:
        self.m1 = Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_model_1_creation_no_event(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        ModelNoEvent.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019,1,1)
        )
        dispatcher.assert_not_called()

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_model_1_creation_event_called(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        m = Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )
        mock.assert_called_once()
        dispatcher.assert_called_with(
            'test_service',
            'model1__created',
            {
                'id': m.id,
                'int_field': 10,
                'char_field': 'test',
            }
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_model_1_updated(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        self.m1.int_field = 300
        self.m1.save()
        mock.assert_called_once()
        dispatcher.assert_called_with(
            'test_service',
            'model1__updated',
            {
                'id': self.m1.id,
                'int_field': 300,
                'char_field': 'test',
            }
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_model_1_deleted(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        m1_id = self.m1.id
        self.m1.delete()
        mock.assert_called_once()
        dispatcher.assert_called_with(
            'test_service',
            'model1__deleted',
            {
                'id': m1_id,
                'int_field': 10,
                'char_field': 'test',
            }
        )


class TestStatusModelDispatcher(TestCase):
    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def setUp(self, mock) -> None:
        self.m1 = StatusModel.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1),
            status='created'
        )
        self.m2 = StatusModel2.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1),
            state='created'
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_status_dispatched(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        m = StatusModel.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1),
            status='created'
        )
        dispatcher.assert_called_with(
            'test_service',
            'status_model__created',
            {
                'id': m.id,
                'int_field': 10,
                'char_field': 'test',
                'uuid_field': str(m.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'created'
            }
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_different_status_on_creation(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        m = StatusModel.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1),
            status='modified'
        )
        dispatcher.assert_called_with(
            'test_service',
            'status_model__modified',
            {
                'id': m.id,
                'int_field': 10,
                'char_field': 'test',
                'uuid_field': str(m.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'modified'
            }
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_status_change_dispatched(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        self.m1.status = 'failed'
        self.m1.int_field = 1000
        self.m1.save()
        dispatcher.assert_called_with(
            'test_service',
            'status_model__failed',
            {
                'id': self.m1.id,
                'int_field': 1000,
                'char_field': 'test',
                'uuid_field': str(self.m1.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'failed'
            }
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_model_deleted_dispatched(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        m1_id = self.m1.id
        self.m1.delete()
        dispatcher.assert_called_with(
            'test_service',
            'status_model__deleted',
            {
                'id': m1_id,
                'int_field': 10,
                'char_field': 'test',
                'uuid_field': str(self.m1.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'created'
            }
        )

    @patch('django_events_sourcing.nameko.events.event_dispatcher')
    def test_model_different_state_field_name(self, mock):
        dispatcher = MagicMock()
        mock.return_value = dispatcher
        self.m2.state = 'failed'
        self.m2.int_field = 44
        self.m2.save()
        dispatcher.assert_called_with(
            'test_service',
            'status_model2__failed',
            {
                'id': self.m2.id,
                'int_field': 44,
                'char_field': 'test',
                'uuid_field': str(self.m2.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'state': 'failed'
            }
        )
