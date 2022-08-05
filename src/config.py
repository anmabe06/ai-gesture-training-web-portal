import os

import environ

from mediapipe.python.solutions.pose import PoseLandmark


env = environ.Env()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # two levels up (../..)

environ.Env.read_env(os.path.join(ROOT_DIR, '.env'))

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = env('AWS_S3_BUCKET_NAME')
LOCAL_DATA_PATH = env('LOCAL_DATA_DIR', default=os.path.join(ROOT_DIR, 'data'))
ORIGINAL_VIDEO_SAMPLE_PREFIX = env('ORIGINAL_VIDEO_SAMPLE_PREFIX', default='sample')
PREFIX_DIGITS_NUM = env('PREFIX_DIGITS_NUM', default=4)
LOCAL_FILES_IGNORED = env.list('LOCAL_FILES_IGNORED', default=(
    '*.DS_Store',
    '.DS_Store',
))
MEDIAPIPE_MIN_DETECTION_CONFIDENCE = env.float('MEDIAPIPE_MIN_CONFIDENCE', 0.5)
MEDIAPIPE_MIN_TRACKING_CONFIDENCE = env.float('MEDIAPIPE_MIN_TRACKING_CONFIDENCE', 0.5)
MEDIAPIPE_INCLUDE_Z_AXIS = env.bool('MEDIAPIPE_INCLUDE_Z_AXIS', default=False)

MEDIAPIPE_LANDMARKS_TO_AVOID_POSE = (
    PoseLandmark.LEFT_EYE_INNER,
    PoseLandmark.LEFT_EYE_OUTER,
    PoseLandmark.RIGHT_EYE_INNER,
    PoseLandmark.RIGHT_EYE_OUTER,
)

MEDIAPIPE_LANDMARKS_TO_AVOID_POSE_WITH_HANDS = (
    *MEDIAPIPE_LANDMARKS_TO_AVOID_POSE,

    PoseLandmark.LEFT_WRIST,
    PoseLandmark.LEFT_PINKY,
    PoseLandmark.LEFT_INDEX,
    PoseLandmark.LEFT_THUMB,

    PoseLandmark.RIGHT_WRIST,
    PoseLandmark.RIGHT_PINKY,
    PoseLandmark.RIGHT_INDEX,
    PoseLandmark.RIGHT_THUMB,
)

MEDIAPIPE_SINGLE_HAND_SIDE = 'right'
