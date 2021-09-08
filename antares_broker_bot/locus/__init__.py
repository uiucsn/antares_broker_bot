from antares_client._api.models import Locus
from prettytable import PrettyTable


BANDS = ('r', 'g')


async def compose_message_from_locus(locus: Locus) -> str:
    table = PrettyTable()
    table.add_column('', ['amplitude', 'mean'])
    for band in BANDS:
        table.add_column(
            f'**{band}**',
            [
                locus.properties[f'feature_amplitude_magn_{band}'],
                locus.properties[f'feature_weighted_mean_magn_{band}'],
            ],
        )

    return f'''**{locus.locus_id}**
    ```text
    {table.get_string(float_format='.2')}
    ```
    https://antares.noirlab.edu/loci/{locus.locus_id}'''
