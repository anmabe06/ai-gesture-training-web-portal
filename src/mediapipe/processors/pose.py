from mediapipe.python.solutions import (
    pose as mp_pose,
    drawing_utils as mp_drawing,
    drawing_styles as mp_drawing_styles,
)

from ..mediapipe_processor import MediapipeProcessor


class PoseProcessor(MediapipeProcessor):
    PROCESSOR_CLASS = mp_pose.Pose
    LANDMARKS_COUNT = 33

    def __init__(self, *args, name='pose', **kwargs):
        super().__init__(name, *args, **kwargs)

    def get_landmarks(self):
        pass

    def draw_landmarks(self, image):
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        # image.flags.writeable = False
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_drawing.draw_landmarks(
            image,
            self.landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )
