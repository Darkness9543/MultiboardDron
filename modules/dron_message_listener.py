import threading
import time


def start_message_listener(self):
    if self.listener_thread is None:
        self.listener_thread = threading.Thread(target=self.message_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()

def message_listener(self):
    while True:
        message = self.vehicle.recv_match(blocking=True)
        if message:
            message_type = message.get_type()
            if message_type == 'PARAM_VALUE':
                param_id = message.param_id.rstrip('\x00')
                self.params_dict[param_id] = message.param_value
            else:
                # If you want to handle other messages, do it here
                pass
        else:
            time.sleep(0.01)  # Prevents tight loop in case of no messages