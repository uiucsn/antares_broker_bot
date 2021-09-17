from aiogram.utils.markdown import escape_md
from antares_client._api.models import Locus
from prettytable import PrettyTable


BANDS = ('r', 'g')


async def compose_message_from_locus(locus: Locus) -> str:
    table = PrettyTable()
    table.add_column('', ['amplitude', 'mean'])
    for band in BANDS:
        table.add_column(
            f'{band}',
            [
                locus.properties[f'feature_amplitude_magn_{band}'],
                locus.properties[f'feature_weighted_mean_magn_{band}'],
            ],
        )
    table.float_format = '.2'
    table_str = escape_md(table.get_string())

    return rf'''https://antares\.noirlab\.edu/loci/{locus.locus_id}
```text
{table_str}
```'''
