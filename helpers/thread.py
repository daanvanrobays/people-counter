import cv2
import threading
import queue
from typing import Optional


class ThreadingClass:
    """
    A class to handle video capture using threading to reduce frame lag.
    """

    def __init__(self, name: str):
        """
        Initialize the threading class with a video source.

        :param name: The video source, typically a filename or camera index.
        """
        self.cap = cv2.VideoCapture(name)
        if not self.cap.isOpened():
            raise ValueError("Error opening video stream or file")

        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()
        self.running = True

    def _reader(self) -> None:
        """
        Read frames from the video source as soon as they are available and store them in a queue.
        This approach reduces the frame lag by avoiding OpenCV's internal buffer.
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self) -> Optional:
        """
        Fetch frames from the queue one by one.

        :return: The next frame from the queue.
        """
        return self.q.get()

    def release(self) -> None:
        """
        Release the video capture resource and stop the reader thread.
        """
        self.running = False
        self.thread.join()
        self.cap.release()
