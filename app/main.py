#Import libraries
import requests
import uvicorn
import os
from fastapi import FastAPI, Query, Body
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv
from utils import bfs_shortest_path

#Load environment variables
load_dotenv()

#Create the app
app = FastAPI()

api_url = os.getenv("API_URL")

#----------------------------------------------------------------------
#1. Analisis de Vecindad
#----------------------------------------------------------------------
@app.get("/countries/{code}/neighbors")
def analisis_vecindad(code: str):
    try:
        url = f"{api_url}/alpha/{code}"
        response = requests.get(url)

        if response.status_code == 200:
            country_data = response.json()

            #Country data its a list
            if isinstance(country_data, list):
                country_data = country_data[0]

            country_languages = set(country_data.get("languages", {}).values())

            borders = country_data.get("borders", [])

            #If no borders, return message
            if not borders:
                return {"message": "This country has no neighboring countries."}
            #Get name, capital, population, total population of neighbors, list of neighbors which share the same language
            neighbors_info = []
            total_population = 0
            shared_language_neighbors = []

            for border in borders:
                neighbor_url = f"{api_url}/alpha/{border}"
                neighbor_response = requests.get(neighbor_url)

                if neighbor_response.status_code == 200:
                    neighbor_data = neighbor_response.json()

                    #Neighbor data its a list
                    if isinstance(neighbor_data, list):
                        neighbor_data = neighbor_data[0]

                    neighbors_info.append({
                        "name": neighbor_data.get("name").get("common"),
                        "capital": neighbor_data.get("capital")[0],
                        "population": neighbor_data.get("population")
                    })
                    
                    total_population += neighbor_data.get("population", 0)

                    #Check for shared languages
                    n_languages = set(neighbor_data.get("languages", {}).values())

                    if country_languages.intersection(n_languages):
                        shared_language_neighbors.append(neighbor_data.get("name").get("common"))
            return {
                "neighbors": neighbors_info,
                "total_population_neighbors": total_population,
                "shared_language_neighbors": shared_language_neighbors
            }
        else:
            return {"error": "Country not found"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# ----------------------------------------------------------------------
#2. Rutas terrestres
#----------------------------------------------------------------------
@app.get("/route")
#Data comes from query parameters
def rutas_terrestres(
    from_: str = Query(..., alias="from"),
    to: str = Query(..., alias="to")
):
    
    #Get all countries data and their borders
    try:
        url = f"{api_url}/all?fields=borders,cca3"
        response = requests.get(url)

        if response.status_code == 200:
            countries_data = response.json()

            #Create a graph of countries and their borders
            graph = {}
            for country in countries_data:
                cioc = country.get("cca3")
                borders = country.get("borders", [])
                if cioc:
                    graph[cioc] = borders

            #Check if both countries exist in the graph
            if from_ not in graph or to not in graph:
                return {"error": "One or both country codes are invalid."}
            
            #BFS to find the shortest path
            result = bfs_shortest_path(graph, from_, to)
            return result 
        else:
            return {"error": "Failed to retrieve countries data."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


#----------------------------------------------------------------------
#3. Estadisticas regionales
#----------------------------------------------------------------------
@app.get("/region/{region}/stats")
def estadisticas_regionales(region: str):
    total_countries = 0
    total_population = 0
    mean_population = 0
    unique_languages = set()

    #Top 5
    most_populous_country = None #Name and population
    ranked_countries = []
    url = f"{api_url}/region/{region}"
    try: 
        response = requests.get(url)

        if response.status_code == 200:
            countries_data = response.json()

            total_countries = len(countries_data)

            if total_countries == 0:
                return {"message": "No countries found in this region."}

            for country in countries_data:
                population = country.get("population", 0)
                total_population += population

                #Get unique languages
                languages = country.get("languages", {})
                for lang in languages.values():
                    unique_languages.add(lang)

            #Round mean population to 2 decimals
            mean_population = round(total_population / total_countries if total_countries > 0 else 0, 2)

            ranked_countries = sorted(
                countries_data,
                key=lambda c: c.get("population", 0),
                reverse=True  # from highest to lowest
            )

            top_5 = ranked_countries[:5]

            #Get just name and population
            top_5 = [
                {
                    "name": country.get("name", {}).get("common"),
                    "population": country.get("population", 0)
                }
                for country in top_5
            ]
            
            #Return the stats
            return {
                "total_countries": total_countries,
                "total_population": total_population,
                "mean_population": mean_population,
                "unique_languages": len(list(unique_languages)),
                "most_populous_country": top_5,
            }
        else:
            return {"error": "Region not found"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


#----------------------------------------------------------------------
#4. Busqueda avanzada
#----------------------------------------------------------------------

#Define the body model
class BodyModel(BaseModel):
    min_population: Optional[int] = None
    max_population: Optional[int] = None
    languages: Optional[List[str]] = None
    region: Optional[str] = None

@app.post("/countries/search")
def busqueda_avanzada(body: Optional[BodyModel] = Body(None)):
    # Filter out None values from the body
    if body is None:
        filters = {}
    else:
        filters = {k: v for k, v in body.dict().items() if v is not None}

    #Apply filters to the countries data
    try:
        url = f"{api_url}/all?fields=name,population,languages,region"
        response = requests.get(url)

        if response.status_code == 200:
            countries_data = response.json()

            filtered_countries = []

            for country in countries_data:
                population = country.get("population", 0)
                languages = set(country.get("languages", {}).values())
                country_region = country.get("region", "")

                # Apply filters, skip if any filter does not match. Because of "and" logic
                if "min_population" in filters and population < filters["min_population"]:
                    continue
                if "max_population" in filters and population > filters["max_population"]:
                    continue
                if "languages" in filters and not languages.intersection(set(filters["languages"])):
                    continue
                if "region" in filters and country_region != filters["region"]:
                    continue
                filtered_countries.append({
                    "name": country.get("name", {}).get("common"),
                    "population": population,
                    "languages": list(languages),
                    "region": country_region
                })

            #return json
            return filtered_countries
        else:
            return {"error": "Failed to retrieve countries data."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
        
#Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)