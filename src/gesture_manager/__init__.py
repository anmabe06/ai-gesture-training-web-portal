from src import config
from src.mediapipe.mediapipe_handler import MediapipeHandler
from src.mediapipe.processors.hands import (
    SingleHandProcessor,
    MultiHandProcessor,
)
from src.mediapipe.processors.pose import PoseProcessor
from src.s3_manager import S3Manager
from .enums import GestureNamespaceEnum


s3_mgr = S3Manager(
    config.AWS_ACCESS_KEY_ID,
    config.AWS_SECRET_ACCESS_KEY,
    config.AWS_S3_BUCKET_NAME
)

mp_options_base = dict(
    min_detection_confidence=config.MEDIAPIPE_MIN_DETECTION_CONFIDENCE,
    min_tracking_confidence=config.MEDIAPIPE_MIN_TRACKING_CONFIDENCE,
)

mp_options_body = mp_options_base

mp_options_hands_base = dict(
    mp_options_base,
    model_complexity=1
)

mp_options_hands_single = dict(
    mp_options_hands_base,
    max_num_hands=1
)

mp_options_hands_multi = dict(
    mp_options_hands_base,
    max_num_hands=2
)

def __build_pose_processor(landmarks_to_avoid=None):
    return PoseProcessor(
        mp_options_body,
        name=GestureNamespaceEnum.BODY,
        landmarks_to_avoid=landmarks_to_avoid,
    )

def __build_single_hand_processor(landmarks_to_avoid=None):
    return SingleHandProcessor(
        config.MEDIAPIPE_SINGLE_HAND_SIDE,
        mp_options_hands_single,
        name=GestureNamespaceEnum.SINGLE_HAND,
        landmarks_to_avoid=landmarks_to_avoid
    )

def __build_multi_hand_processor(landmarks_to_avoid=None):
    return MultiHandProcessor(
        mp_options_hands_multi,
        name=GestureNamespaceEnum.MULTI_HAND,
        landmarks_to_avoid=landmarks_to_avoid
    )


mediapipe_handlers=dict()

# body

mediapipe_handlers[GestureNamespaceEnum.BODY] = MediapipeHandler(
    processors=(
        __build_pose_processor(config.MEDIAPIPE_LANDMARKS_TO_AVOID_POSE),
    )
)

# single hand

mediapipe_handlers[GestureNamespaceEnum.SINGLE_HAND] = MediapipeHandler(
    processors=(
        __build_single_hand_processor(),
    )
)
mediapipe_handlers[GestureNamespaceEnum.SINGLE_HAND_BODY] = MediapipeHandler(
    processors=(
        __build_single_hand_processor(),
        __build_pose_processor(config.MEDIAPIPE_LANDMARKS_TO_AVOID_POSE_WITH_HANDS)
    )
)

# multi hand

mediapipe_handlers[GestureNamespaceEnum.MULTI_HAND] = MediapipeHandler(
    processors=(
        __build_multi_hand_processor(),
    )
)
mediapipe_handlers[GestureNamespaceEnum.MULTI_HAND_BODY] = MediapipeHandler(
    processors=(
        __build_multi_hand_processor(),
        __build_pose_processor(config.MEDIAPIPE_LANDMARKS_TO_AVOID_POSE_WITH_HANDS)
    )
)
