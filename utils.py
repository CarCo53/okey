import random
from log import logger

@logger.log_function
def benzersiz_id_uret():
    """Benzersiz bir ID üretir (taşlar için)."""
    return random.randint(100000, 999999)