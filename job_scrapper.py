# Pour extraire une partie des données sur indeed.com

import pandas as pd
import requests
from bs4 import BeautifulSoup

def job_scrapper(poste: str, lieu: str, site="https://fr.indeed.com/", npages=5) -> pd.DataFrame:
    """Pour extraire les informations d'offres d'emplois sur indeed.com

    Args:
        poste (_type_): Type de poste recherché.
        lieu (_type_): Localisation du poste recherché.
        site (str, optional): Site d'emplois à utiliser comme source de données. Defaults to "https://fr.indeed.com/".
        npages (int, optional): Parcourir les n-premières pages. Defaults to 5.
    """

    poste = poste.replace(" ", "%20") # %20 pour espace
    lieu = lieu.replace(" ", "%20")

    url = f"{site}emplois?q={poste}&l={lieu}"
    print(f"Requête de url = {url}")

    def scrap_page(url):
        """Pour récupérer la description des emplois sur une page web de indeed.com.

        Args:
            url (str): L'adresse url cible.

        Returns:
            pd.DataFrame: Tableau de données avec les résultats.
        """
        
        # requête web et création de la "soup"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        def jurl(rr):
            """Pour récupérer l'url vers la description d'un emplois.

            Args:
                rr (soup): Résultat de la sélection ('find') obtenue avec BeautifulSoup 

            Returns:
                str: L'url vers la dscription de l'emploi.
            """
            job_url = [i for i in str(rr).split(" ") if "href" in i]
            try:
                job_url = job_url[0].split(";")[0]
                job_url = job_url[7:] # supprime "href = "
            except Exception as e:
                # si erreur c'est que ce n'est pas un job
                job_url = ""
            return job_url

        # Récupération des "cartes" d'emplois (essais erreur avec devtools de chrome)
        jobs = soup.find_all("h2")
        hrefs = []
        for j in jobs:
            ju = jurl(j)
            if ju != "":
                hrefs.append(site + ju)

        # Itérer ensuite sur sur chaque url de job
        def get_job_desc(job_url):
            """Pour récupérer la description d'un emploi

            Args:
                job_url (str): adresse vers la page web de description de l'emploi.

            Returns:
                str: La description de l'emploi.
            """
            job_desc = requests.get(job_url)
            soup = BeautifulSoup(job_desc.content, "html.parser")
            results = soup.find(id="jobDescriptionText")
            
            return(results.text.strip() if results is not None else None)

        job_desc = []
        for jj in hrefs:
            job_desc.append(get_job_desc(jj))

        # Intégrer le résultat dans un dataframe
        res = pd.DataFrame(dict(lien=hrefs, job_desc=job_desc))
        return res

    res = scrap_page(url)
    for i in range(1, npages):
        next_url = url + f"&start={10*i}"
        print(f"next_url = {next_url}")
        try:
            nres = scrap_page(next_url)
            res = pd.concat([res, nres])
        except Exception as e:
            print(e)
            break
            
    return(res)

if __name__ == "__main__":
    res = job_scrapper(poste="Data engineer", lieu="Paris", npages=1)
    print(res)
