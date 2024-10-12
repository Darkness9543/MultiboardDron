import threading
import queue
from pymavlink import mavutil

class MessageHandler:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.handlers = {}
        self.lock = threading.Lock()
        self.running = True
        self.waiting_threads = []

        self.thread = threading.Thread(target=self._message_loop)
        self.thread.daemon = True
        self.thread.start()

    def _message_loop(self):
        while self.running:
            msg = self.vehicle.recv_match(blocking=True, timeout=1)
            if msg:
                msg_type = msg.get_type()

                # Handle synchronous waits
                with self.lock:
                    for waiting in self.waiting_threads:
                        if waiting['msg_type'] == msg_type and (waiting['condition'] is None or waiting['condition'](msg)):
                            waiting['queue'].put(msg)
                            self.waiting_threads.remove(waiting)
                            break  # Remove only one waiting thread per message

                # Dispatch message to registered handlers
                if msg_type in self.handlers:
                    for callback in self.handlers[msg_type]:
                        callback(msg)

    def register_handler(self, msg_type, callback):
        with self.lock:
            if msg_type not in self.handlers:
                self.handlers[msg_type] = []
            self.handlers[msg_type].append(callback)

    def unregister_handler(self, msg_type, callback):
        with self.lock:
            if msg_type in self.handlers and callback in self.handlers[msg_type]:
                self.handlers[msg_type].remove(callback)
                if not self.handlers[msg_type]:
                    del self.handlers[msg_type]

    def wait_for_message(self, msg_type, condition=None, timeout=None):
        msg_queue = queue.Queue()
        waiting = {
            'msg_type': msg_type,
            'condition': condition,
            'queue': msg_queue
        }
        with self.lock:
            self.waiting_threads.append(waiting)
        try:
            msg = msg_queue.get(timeout=timeout)
        except queue.Empty:
            msg = None
        return msg

    def stop(self):
        self.running = False
        self.thread.join()
