from src.enums import CustomEnum


class GestureNamespaceEnum(str, CustomEnum):
    BODY = 'body'
    SINGLE_HAND = 'single-hand'
    SINGLE_HAND_BODY = 'single-hand-body'
    MULTI_HAND = 'multi-hand'
    MULTI_HAND_BODY = 'multi-hand-body'


class GestureSubdirEnum(str, CustomEnum):
    ORIGINAL = 'original'
    LANDMARKED = 'landmarked'
    CSV = 'csv'
