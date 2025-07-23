# coding: utf-8
# 

import wda
import threading


def test_callback(app: wda.Client):
    event = threading.Event()
    def _cb(client: wda.Client, url: str):
        if url.endswith("/sendkeys"):
            pass
        assert isinstance(client, wda.Client)
        assert url.endswith("/status")
        event.set()

    app.register_callback(wda.Callback.HTTP_REQUEST_BEFORE, _cb)
    # app.register_callback(wda.Callback.HTTP_REQUEST_AFTER, lambda url, response: print(url, response))
    app.status()
    assert event.is_set(), "callback is not called"

    # test remove_callback
    event.clear()
    app.unregister_callback(wda.Callback.HTTP_REQUEST_BEFORE, _cb)
    app.status()
    assert not event.is_set(), "callback is should not be called"

    event.clear()
    app.unregister_callback(wda.Callback.HTTP_REQUEST_BEFORE)
    app.status()
    assert not event.is_set(), "callback is should not be called"

    event.clear()
    app.unregister_callback()
    app.status()
    assert not event.is_set(), "callback is should not be called"