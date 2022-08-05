import os

from abc import ABC, abstractmethod

from src.logger import logger
from src.mediapipe.processors import ProcessorException


class MediapipeProcessor(ABC):
    PROCESSOR_CLASS = None
    LANDMARKS_COUNT = None

    def __init__(self, name, mp_options, landmarks_to_avoid=None,
                 include_z_axis=False, use_px_coordinates=True):
        self.name = name
        self.mp_options = mp_options
        self.landmarks_to_avoid = landmarks_to_avoid or []
        self.include_z_axis = include_z_axis
        self.use_px_coordinates = use_px_coordinates

        self.data = []
        self.image = None
        self.landmarks = None
        self.result = None
        self.csv_dir_path = None

    def __init_subclass__(cls):
        if cls.PROCESSOR_CLASS == None or cls.LANDMARKS_COUNT == None:
            raise Exception(
                f'class {cls.__module__}.{cls.__name__} is a subclass '
                'of MediapipeProcessor and must have all superclass static properties defined'
            )

    @abstractmethod
    def draw_landmarks(self, image):
        "Draw landsmarks over given image"
        pass

    @abstractmethod
    def get_landmarks(self):
        "Returns all landmarks needed to draw over image and save to csv"
        pass

    def _get_image_dimensions(self):
        height, width, color = self.image.shape
        return height, width

    def _convert_landmark_to_px(self, landmark):
        "Not used so far because not compatible with z axis values"
        width, height = self._get_image_dimensions()
        return [
            int(landmark.x * width),
            int(landmark.y * height),

            # todo: not working so far, dig further
            # https://google.github.io/mediapipe/solutions/hands.html#multi_hand_landmarks
            # https://www.google.com/search?q=denormalize+z+axis+mediapipe&oq=denormalize+z+axis+mediapipe&aqs=chrome..69i57j33i10i160.8985j0j7&sourceid=chrome&ie=UTF-8
            int(landmark.z) * width
        ]

    def _is_valid_lm_group(self, lm_group):
        "Checks if given lm_group (right hand, pose, etc) has same landmarks count as expected"
        lm_detected_count = len(lm_group.landmark)
        lm_expected_count = self.LANDMARKS_COUNT - len(self.landmarks_to_avoid)

        if lm_detected_count > lm_expected_count:
            logger.critical(
                'Processor detected more landmarks than minimum expected! '
                'Please check if you are doing something wrong in code and/or samples'
            )

        return lm_detected_count == lm_expected_count

    def _get_landmarks_data(self):
        """Returns landmarks data ready to be saved"""
        def get_landmark_data(landmark):
            if self.use_px_coordinates:
                x, y, z = self._convert_landmark_to_px(landmark)
            else:
                x, y, z = (landmark.x, landmark.y, landmark.z)

            if self.include_z_axis:
                return x, y, z

            return x, y

        data = []
        for lm_group in self.landmarks:
            if not self._is_valid_lm_group(lm_group):
                continue

            for lm_index, landmark in enumerate(lm_group.landmark):
                if lm_index in self.landmarks_to_avoid:
                    continue
                data.extend(get_landmark_data(landmark))
        return data

    def _remove_landmarks_to_avoid(self, lm_group):
        """Removes landmarks from given lm_group which have with same indexes as
        defined in landmarks_to_avoid"""
        for lm_idx_to_avoid in self.landmarks_to_avoid:
            del lm_group.landmark[lm_idx_to_avoid]

    @property
    def has_landmarks(self):
        return self.landmarks is not None

    @property
    def csv_file_path(self):
        return os.path.join(self.csv_dir_path, f'{self.name}.csv')

    def start(self):
        self.mp_instance = self.PROCESSOR_CLASS(**self.mp_options)

    def process(self, image):
        try:
            self.image = image
            self.result = self.mp_instance.process(image)
            self.landmarks = self.get_landmarks()
            self.draw_landmarks(image)
            self.data = self._get_landmarks_data()
        except ProcessorException as e:
            raise ProcessorException(f'{self.__class__.__name__} - {str(e)}')

    def close(self):
        self.mp_instance.close()
