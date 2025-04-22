from mastodon import Mastodon
import os

MASTODON_BASE_URL = "https://remember.elbarand.pics"
ACCESS_TOKEN = "aELxW5yQ1DW2_Ko9Z6eYF0U8IUewtgWbPHoDB4GhFRc"

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=MASTODON_BASE_URL
)
