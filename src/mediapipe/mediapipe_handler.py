import cv2

from typing import List

from src.file_manager import FileManager
from src.logger import logger
from .mediapipe_processor import MediapipeProcessor
from .processors import ProcessorException


class MediapipeHandler:
    def __init__(
        self,
        processors: List[MediapipeProcessor]
    ):
        self.processors = processors
        self.csv_file_path = None

    def set_csv_file_path(self, path):
        self.csv_file_path = path

    def start_processors(self):
        for processor in self.processors:
            processor.start()

    def process_image(self, image):
        data = []
        try:
            for processor in self.processors:
                processor.process(image)
                data.extend(processor.data)
            FileManager.append_row_to_csv_file(data, self.csv_file_path)
        except ProcessorException as e:
            line_num = FileManager.count_file_lines(self.csv_file_path)
            logger.warning(
                f'Failed to process image for csv line {line_num}. Reason: {str(e)}'
            )

    def close_processors(self):
        for processor in self.processors:
            processor.close()

    def process_video(self, input_video, output_video):

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        cap = cv2.VideoCapture(input_video)

        # Get dimensions of original video
        input_video_width  = int(cap.get(3))
        input_video_height = int(cap.get(4))
        out = cv2.VideoWriter(output_video, fourcc, 20, (input_video_width, input_video_height))

        FileManager.remove_file_if_exists(self.csv_file_path)
        self.start_processors()

        while cap.isOpened():
            ret, image = cap.read()
            if not ret:
                break

            image = cv2.flip(image, 1) # selfie mode

            self.process_image(image)

            cv2.imshow('video', image)
            out.write(image)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                break

        cap.release()
        logger.success(f'Finished processing video {input_video}')

        self.close_processors()
