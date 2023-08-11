from cat.mad_hatter.decorators import tool, hook
from cat.log import log
from cat.memory.vector_memory import VectorMemory

import requests
from bs4 import BeautifulSoup

@tool
def aggiorna(none,cat):
    """use the tool only when the phrase "update the documentation" is used the phrase must be used alone."""
    url = 'https://cheshire-cat-ai.github.io/docs/'
    
    collections=VectorMemory(cat).collections['declarative']
    
    memorys=collections.get_all_points()
    
    links_id_list=[]
    for memory in memorys:
        id=''
        for i in memory:
            
            if "'id'" in str(i):
                id=str(i[1])
                
            if "'source':" in str(i):
                for ii in i:
                    if "'source':" in str(ii):
                        if 'https://cheshire-cat-ai.github.io/docs/' in str(ii['metadata']['source']):
                            log('added to watch list: '+str(ii['metadata']['source']), "WARNING")
                            links_id_list.append(
                                {
                                    "id": [id],
                                    "link": ii['metadata']['source']
                                }
                            )
        
                      
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
                
                for links_id in links_id_list:
                    if link == links_id['link']:
                        log("link already exists \n deleting...", "WARNING")
                        collections.delete_points(links_id['id'])
                        log("deleted...", "WARNING")

                cat.rabbit_hole.ingest_file(link, chunk_size=400, chunk_overlap=100)

                log(link + " sent to rabbithole!", "WARNING")
                message = message + "<tr><td>" + link + "</td><td>&#x2705;</td></tr>"
            except requests.exceptions.RequestException as err:
                message = message + "<tr><td>" + link + "</td><td>&#x274C; " + str(err) + "</td></tr>"
    message = message + "</tbody></table>"

    return message