from cat.mad_hatter.decorators import tool, hook
from cat.log import log

import requests
from bs4 import BeautifulSoup

@tool
def aggiorna(none,cat):
    """Replies to 'update documentation'."""
    url = 'https://cheshire-cat-ai.github.io/docs/'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select('.md-nav__list a')

    unique_links = set()

    for link in links:
        if '#' not in link['href']:
            unique_links.add(url+link['href'])

    message = "<table><thead><tr><th class=\"text-neutral\">URL</th><th class=\"text-neutral\">Status</th></tr></thead><tbody>"
    for link in unique_links:
        if not link.startswith(('http://', 'https://')):
            message = message + link + ": Invalid link format: must start with 'http://' or 'https://'\n"
        else:
            try:
                log("Send " + link + " to rabbithole", "WARNING")

                cat.rabbit_hole.ingest_url(link, chunk_size=400, chunk_overlap=100, summary=False)

                
                log(link + " sent to rabbithole!", "WARNING")
                message = message + "<tr><td>" + link + "</td><td>&#x2705;</td></tr>"
            except requests.exceptions.RequestException as err:
                message = message + "<tr><td>" + link + "</td><td>&#x274C; " + str(err) + "</td></tr>"
    message = message + "</tbody></table>"

    return message