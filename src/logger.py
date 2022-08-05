import coloredlogs
import logging
import verboselogs

# verboselogs.install()
logger = logging.getLogger("chiara-gesture")
logger = verboselogs.VerboseLogger('chiara-gesture')
logger.addHandler(logging.StreamHandler())
logger.setLevel(verboselogs.VERBOSE)

# https://coloredlogs.readthedocs.io/en/latest/api.html#coloredlogs.install
coloredlogs.install(
    logger=logger,
    level=logging.DEBUG,
    # fmt="[%(levelname)s] [(%(threadName)s)] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s",
    # fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
    fmt="%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
    # datefmt="%H:%M:%S",
    level_styles=coloredlogs.DEFAULT_LEVEL_STYLES.update(
        dict(
            # critical=dict(color='white', bold=True, background='red'),
        )
    ),
    field_styles=coloredlogs.DEFAULT_FIELD_STYLES.update(
        dict(
            levelname=dict(bold=True, color='white', background='black'),
        )
    ),
    milliseconds=True
)

# https://verboselogs.readthedocs.io/en/latest/readme.html#overview-of-logging-levels
# logger.spam('message with level spam')
# logger.debug('message with level debug')
# logger.verbose('message with level verbose')
# logger.info('message with level info')
# logger.notice('message with level notice')
# logger.warning('message with level warning')
# logger.success('message with level success')
# logger.error('message with level error')
# logger.critical('message with level critical')
