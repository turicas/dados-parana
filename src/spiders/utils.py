"""
Utility functions
"""

import re


REGEXP_CAMELCASE_TO_UNDERSCORE = re.compile("([a-z])([A-Z])")


def normalize_key(key):
    """Transform name from camelCase to underscore and replace abbreviations"""

    return (
        REGEXP_CAMELCASE_TO_UNDERSCORE.sub(r"\1_\2", key)
        .lower()
        .replace("cd_", "codigo_")
        .replace("nm_", "nome_")
        .replace("nr_", "numero_")
        .replace("vl_", "valor_")
        .replace("dt_", "data_")
        .replace("ds_", "descricao_")
    )
