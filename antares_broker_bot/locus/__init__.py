from antares_client._api.models import Locus


async def compose_message_from_locus(locus: Locus) -> str:
    return f'https://antares.noirlab.edu/loci/{locus.locus_id}'
