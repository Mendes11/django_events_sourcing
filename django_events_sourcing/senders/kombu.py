from contextlib import contextmanager

import amqp
from kombu import Exchange, Connection, producers, Producer

DEFAULT_HEARTBEAT = 60
DEFAULT_TRANSPORT_OPTIONS = {
    'max_retries': 3,
    'interval_start': 2,
    'interval_step': 1,
    'interval_max': 5
}
DEFAULT_RETRY_POLICY = {'max_retries': 3}

default_transport_options = {
    'confirm_publish': True
}


def get_exchange(service_name):
    exchange_name = "%s.events" % service_name
    return Exchange(exchange_name, type='topic', auto_delete=True)



def dispatch(
        service_name, event_name, payload, amqp_uri, ssl=None,
        transport_options=None, heartbeat=60,
):
    """
    Dispatches an event. It mimics Nameko's and Micro-Framework's format of
    receiving events.

    :param event_name: Name of the Event
    :param payload: Serializable Payload to be sent
    :param amqp_uri: URI to connect to AMQP
    :param service_name: Name of the Service sending the event
    :param ssl: To use SSL or not
    :param transport_options: Transport Options dict
    :param heartbeat: AMQP Heartbeats interval
    """
    try:
        exchange = get_exchange(service_name)

        transport_options = transport_options or default_transport_options
        with producers[
            Connection(
                amqp_uri, ssl=ssl, transport_options=transport_options,
            )
        ].acquire(block=True) as producer:
            producer.publish(
                payload, routing_key=event_name, exchange=exchange,
                retry=True
            )

    except amqp.exceptions.NotFound:
        pass
