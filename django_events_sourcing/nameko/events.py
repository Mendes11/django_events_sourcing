import amqp
from nameko.standalone.events import event_dispatcher
from django.conf import settings


def get_event_dispatcher(nameko_config):
    return event_dispatcher(nameko_config)


def dispatch(event_name, payload, service_name=settings.SERVICE_NAME,
             nameko_config=settings.NAMEKO_CONFIG):
    try:
        dispatcher = get_event_dispatcher(nameko_config)
        dispatcher(service_name, event_name, payload)
    except amqp.exceptions.NotFound:
        # TODO It is interesting to force the creation of the exchange in
        #  rabbit even if no one is listening
        pass
