import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock, call

from django.test import TestCase, override_settings

from django_events_sourcing.register import disable_model_obj_dispatcher
from django_events_sourcing.testing import disable_dispatcher
from tests.test_app.models import Model1, ModelNoEvent, StatusModel, \
    StatusModel2


class TestModelDispatcher(TestCase):
    @patch('django_events_sourcing.dispatcher.dispatch')
    def setUp(self, mock) -> None:
        self.m1 = Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_1_creation_no_event(self, mock):
        ModelNoEvent.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )
        mock.assert_not_called()

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_1_creation_event_called(self, mock):
        m = Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )
        mock.assert_called_once()
        mock.assert_called_with(
            'test_service',
            'model1__created',
            {
                'id': m.id,
                'int_field': 10,
                'char_field': 'test',
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_1_updated(self, mock):
        self.m1.int_field = 300
        self.m1.save()
        mock.assert_called_once()
        mock.assert_called_with(
            'test_service',
            'model1__updated',
            {
                'id': self.m1.id,
                'int_field': 300,
                'char_field': 'test',
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_1_deleted(self, mock):
        m1_id = self.m1.id
        self.m1.delete()
        mock.assert_called_once()
        mock.assert_called_with(
            'test_service',
            'model1__deleted',
            {
                'id': m1_id,
                'int_field': 10,
                'char_field': 'test',
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @override_settings(MODELS_CRUD_EVENT=[])
    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_no_event_dispatched(self, mock):
        Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )
        mock.assert_not_called()

    @override_settings(
        MODELS_CRUD_EVENT=[
            {'model': 'test_app.Model1', "event_name_prefix": "my_model1",
             'serializer': 'tests.test_app.serializers.Model1Serializer'}
        ]
    )
    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_custom_event_name_prefix(self, mock):
        m = Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )
        mock.assert_called_once()
        mock.assert_called_with(
            'test_service',
            'my_model1__created',
            {
                'id': m.id,
                'int_field': 10,
                'char_field': 'test',
            },
            'amqp://guest:guest@localhost:5672/'
        )


class TestStatusModelDispatcher(TestCase):
    @patch('django_events_sourcing.dispatcher.dispatch')
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

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_status_dispatched(self, mock):
        m = StatusModel.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1),
            status='created'
        )
        mock.assert_called_with(
            'test_service',
            'status_model__created',
            {
                'id': m.id,
                'int_field': 10,
                'char_field': 'test',
                'uuid_field': str(m.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'created'
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_different_status_on_creation(self, mock):
        m = StatusModel.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1),
            status='modified'
        )
        mock.assert_called_with(
            'test_service',
            'status_model__modified',
            {
                'id': m.id,
                'int_field': 10,
                'char_field': 'test',
                'uuid_field': str(m.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'modified'
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_status_change_dispatched(self, mock):
        self.m1.status = 'failed'
        self.m1.int_field = 1000
        self.m1.save()
        mock.assert_called_with(
            'test_service',
            'status_model__failed',
            {
                'id': self.m1.id,
                'int_field': 1000,
                'char_field': 'test',
                'uuid_field': str(self.m1.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'failed'
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_deleted_dispatched(self, mock):
        m1_id = self.m1.id
        self.m1.delete()
        mock.assert_called_with(
            'test_service',
            'status_model__deleted',
            {
                'id': m1_id,
                'int_field': 10,
                'char_field': 'test',
                'uuid_field': str(self.m1.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'status': 'created'
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_different_state_field_name(self, mock):
        self.m2.state = 'failed'
        self.m2.int_field = 44
        self.m2.save()
        mock.assert_called_with(
            'test_service',
            'status_model2__failed',
            {
                'id': self.m2.id,
                'int_field': 44,
                'char_field': 'test',
                'uuid_field': str(self.m2.uuid_field),
                'dt_field': '2019-01-01T00:00:00',
                'state': 'failed'
            },
            'amqp://guest:guest@localhost:5672/'
        )


class TestDisableDispatcherDecorator(TestCase):
    @patch('django_events_sourcing.dispatcher.dispatch')
    def setUp(self, mock) -> None:
        self.m1 = Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )
        self.m2 = Model1.objects.create(
            int_field=1,
            char_field='test2',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2020, 1, 1)
        )

    @disable_dispatcher()
    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_all_models_disabled(self, mock):
        self.m1.int_field = 100
        self.m1.save()
        self.m1.delete()
        Model1.objects.create(int_field=200, char_field='test',
                              uuid_field=uuid.uuid4(),
                              dt_field=datetime(2019, 1, 1))
        mock.assert_not_called()

    @disable_dispatcher(models_list=['test_app.Model1'])
    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_1_disabled(self, mock):
        self.m1.int_field = 100
        self.m1.save()
        self.m1.delete()
        StatusModel.objects.create(int_field=200, char_field='test',
                                   uuid_field=uuid.uuid4(),
                                   dt_field=datetime(2019, 1, 1))
        mock.assert_called_once()

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_object_disabled(self, dispatcher):
        with disable_model_obj_dispatcher(self.m2):
            self.m1.int_field = 100
            self.m1.save()
            self.m2.int_field = 100
            self.m2.save()
        dispatcher.assert_called_once()
        dispatcher.assert_called_with(
            "test_service",
            "model1__updated",
            {
                'id': self.m1.id,
                'int_field': 100,
                'char_field': 'test',
            },
            'amqp://guest:guest@localhost:5672/'
        )

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_obj_restored(self, dispatcher):
        with disable_model_obj_dispatcher(self.m2):
            self.m1.int_field = 100
            self.m1.save()
            self.m2.int_field = 100
            self.m2.save()
        self.m2.int_field = 0
        self.m2.save()
        dispatcher.assert_has_calls(
            [
                call(
                    "test_service", "model1__updated",
                    {'id': self.m1.id, 'int_field': 100, 'char_field': 'test'},
                    'amqp://guest:guest@localhost:5672/'
                ),
                call(
                    "test_service", "model1__updated",
                    {'id': self.m2.id, 'int_field': 0, 'char_field': 'test2'},
                    'amqp://guest:guest@localhost:5672/'
                ),
            ]
        )


@disable_dispatcher()
class TestDisableDispatcherClassDecoratorAllModels(TestCase):
    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_nothing_dispatched(self, mock):
        StatusModel.objects.create(int_field=200, char_field='test',
                                   uuid_field=uuid.uuid4(),
                                   dt_field=datetime(2019, 1, 1))
        mock.assert_not_called()


@disable_dispatcher(models_list=['test_app.Model1'])
class TestDisableDispatcherClassDecoratorModel1(TestCase):
    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_model_1_not_dispatched(self, mock):
        self.m1 = Model1.objects.create(
            int_field=10,
            char_field='test',
            uuid_field=uuid.uuid4(),
            dt_field=datetime(2019, 1, 1)
        )
        mock.assert_not_called()

    @patch('django_events_sourcing.dispatcher.dispatch')
    def test_status_model_dispatched(self, mock):
        StatusModel.objects.create(int_field=200, char_field='test',
                                   uuid_field=uuid.uuid4(),
                                   dt_field=datetime(2019, 1, 1))
        mock.assert_called_once()
