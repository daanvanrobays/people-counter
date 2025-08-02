import cv2, threading, queue
import time


class ThreadingClass:
    # initiate threading class
    def __init__(self, name, debug_logger=None):
        self.cap = cv2.VideoCapture(name)
        self.stream_url = name
        self.debug_logger = debug_logger
        self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 60000)
        self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 60000)
        # define an empty queue and thread
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read the frames as soon as they are available
    # this approach removes OpenCV's internal buffer and reduces the frame lag
    def _reader(self):
        retry_count = 0
        retry_delay = 5
        max_retries = 5
        while True:
            ret, frame = self.cap.read()  # read the frames and ---
            if not ret:
                if self.debug_logger:
                    self.debug_logger.log_error("Stream timeout or frame read error.")
                retry_count += 1
                if retry_count > max_retries:
                    if self.debug_logger:
                        self.debug_logger.log_error("Maximum retry limit reached. Exiting.")
                    break
                else:
                    if self.debug_logger:
                        self.debug_logger.log_warning(f"Retrying in {retry_delay} seconds... ({retry_count}/{max_retries})")
                    time.sleep(retry_delay)
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.stream_url)
                    continue
            else:
                retry_count = 0
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)  # --- store them in a queue (instead of the buffer)

    def read(self):
        return self.q.get()  # fetch frames from the queue one by one

    def release(self):
        return self.cap.release()  # release the hw resource
