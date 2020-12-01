import pigpio as pigpio
import settings
from threading import Timer
from datetime import datetime, timedelta

from main import app

RELAY_GPIO_PIN = 2
pigpio = pigpio.pi()


def status():
    return 'on' if pigpio.read(RELAY_GPIO_PIN) == 1 else 'off'


def execute(command):
    global off_timer
    app.logger.info(f'coffee.execute({command})')
    if command == 'on':
        if status() == 'on':
            return 400, 'already on'
        else:
            pigpio.write(RELAY_GPIO_PIN, 1)

        if not off_timer.is_alive():
            timeout = settings.coffee_timeout_millis()
            off_timer = build_timer(timeout, 'off')
            app.logger.info(f'\tturning off in {timeout / 60} minutes')
            off_timer.start()

        return 201, 'turned on'
    elif command == 'off':
        if status() == 'off':
            return 400, 'already off'
        else:
            pigpio.write(RELAY_GPIO_PIN, 0)

        off_timer.cancel()
        return 201, 'turned off'
    elif command == 'status':
        return 200, status()
    elif command == 'schedule':
        pass
    return 404, 'no such endpoint'


def build_timer(timeout_mills, arg):
    return Timer(timeout_mills, execute, [arg])


off_timer = build_timer(settings.coffee_timeout_millis(), 'off')
on_timer = None


def time_24h_tostr(t):
    dt_parts = list(map(lambda i: int(i), t.split(':')))
    return timedelta(hours=dt_parts[0], minutes=dt_parts[1])


def schedule(dt):
    global on_timer
    if dt == 'cancel':
        if on_timer is not None:
            on_timer.cancel()
            on_timer = None
            return 201, 'cancelled timer'
        else:
            return 204, 'nothing to cancel'

    now = datetime.today()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    scheduled_time = midnight + time_24h_tostr(dt)
    if now > scheduled_time:
        scheduled_time += timedelta(days=1)
    delta = (scheduled_time - now).total_seconds()

    do_cancel = False
    if on_timer is not None and on_timer.is_alive():
        do_cancel = True
        on_timer.cancel()
    on_timer = build_timer(delta, 'on')
    on_timer.start()
    return 201, f'{"re" if do_cancel else ""}scheduled in {delta / 3600} hours'
