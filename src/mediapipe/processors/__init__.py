from src.enums import CustomEnum


class MediapipeProcessorEnum(str, CustomEnum):
    POSE = 'pose'
    SINGLE_HAND = 'single_hand'
    MULTI_HAND = 'multi_hand'


class ProcessorException(Exception):
    pass