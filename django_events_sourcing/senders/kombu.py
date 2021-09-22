from contextlib import contextmanager

import amqp
from kombu import Exchange, Connection, producers

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


def get_connection(amqp_uri, heartbeat=None, ssl=None, transport_options=None):
    if heartbeat is None: heartbeat = DEFAULT_HEARTBEAT
    if transport_options is None: transport_options = default_transport_options.copy()

    connection = Connection(
        amqp_uri, transport_options=transport_options,
        heartbeat=heartbeat, ssl=ssl
    )
    return connection


@contextmanager
def get_producer(
        amqp_uri, confirms=True, ssl=None, transport_options=None,
        heartbeat=None
):
    if transport_options is None:
        transport_options = DEFAULT_TRANSPORT_OPTIONS.copy()

    transport_options['confirm_publish'] = confirms
    conn = get_connection(
        amqp_uri, heartbeat=heartbeat, ssl=ssl,
        transport_options=transport_options
    )
    with producers[conn].acquire(block=True) as producer:
        yield producer


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
        with get_producer(
                amqp_uri,
                ssl=ssl,
                transport_options=transport_options,
                heartbeat=heartbeat
        ) as producer:
            producer.publish(
                payload, routing_key=event_name, exchange=exchange
            )
    except amqp.exceptions.NotFound:
        pass
