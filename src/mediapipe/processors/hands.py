from mediapipe.python.solutions import (
    hands as mp_hands,
    drawing_utils as mp_drawing,
    drawing_styles as mp_drawing_styles,
)

from src.logger import logger
from ..mediapipe_processor import MediapipeProcessor
from ..processors import ProcessorException


class HandProcessor(MediapipeProcessor):
    LANDMARKS_COUNT = 21
    PROCESSOR_CLASS = mp_hands.Hands

    def draw_landmarks(self, image):
        # Draw the hand annotations on the image.
        # image.flags.writeable = True
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if self.landmarks:
            for hand_landmarks in self.landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )


class SingleHandProcessor(HandProcessor):
    def __init__(self, hand_side, *args, name='single-hand', **kwargs):
        self.hand_side = hand_side
        args = (name, *args)
        super().__init__(*args, **kwargs)

    def get_landmarks(self):
        def get_index():
            logger.debug(f'multi handedness length: {len(self.result.multi_handedness)}')
            for item in self.result.multi_handedness:
                logger.debug(f'classification length: {len(item.classification)}')
                for item_classification in item.classification:
                    logger.debug(f'classification: {item_classification}')
                    if item_classification.label.lower() == self.hand_side.lower():
                        return item_classification.index

        if self.result.multi_handedness is None:
            return None

        index_orig = get_index()
        if index_orig is None:
            return None

        index = 0 if index_orig == 1 else 1
        try:
            logger.debug(f'Multi hand landmarks len: {len(self.result.multi_hand_landmarks)}')
            lm_group = self.result.multi_hand_landmarks[index]
            self._remove_landmarks_to_avoid(lm_group)
            return lm_group
        except IndexError:
            return None


class MultiHandProcessor(HandProcessor):
    def __init__(self, *args, name='multi-hand', **kwargs):
        args = (name, *args)
        super().__init__(*args, **kwargs)

    def get_landmarks(self):
        if self.result.multi_hand_landmarks is None:
            raise ProcessorException('Landmarks not found')

        lm_group_count = len(self.result.multi_hand_landmarks)
        lm_group_count_expected = 2

        if lm_group_count < lm_group_count_expected:
            raise ProcessorException(
                f'Found less landmark groups ({lm_group_count}) than expected ({lm_group_count_expected})'
            )

        if lm_group_count > lm_group_count_expected:
            raise ProcessorException(
                f'More than {lm_group_count_expected} landmark groups were detected ({lm_group_count})'
            )

        for lm_group in self.result.multi_hand_landmarks:
            self._remove_landmarks_to_avoid(lm_group)

        return self.result.multi_hand_landmarks
