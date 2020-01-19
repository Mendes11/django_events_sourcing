from django_events_sourcing.dispatcher import dispatch_event


def generic_post_save(sender, instance, created, **kwargs):
    action = 'created' if created else 'updated'
    dispatch_event(instance, action=action)


def generic_post_delete(sender, instance, **kwargs):
    dispatch_event(instance, action='deleted')
