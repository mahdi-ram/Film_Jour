import requests
import json

def infodata(imdb_id: str):
    def get_data(imdb_id, lang):
        url = f"https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id&language={lang}"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhYTI0NTU0ZDE2Mzc5YjhjY2Q1ZGUxNDNmMDg0YTk2ZCIsIm5iZiI6MTcyMDE5ODg3OS42NjI5NzEsInN1YiI6IjY0MjFhZjNhMmRjOWRjMDA3YzA3MDcxMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VWF7xrk4vvRQFNXN4pDxM-eNHidDTj9-B_3vOkzlRLc"
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)
    
    def extract_info(results, media_type):
        if len(results) == 0:
            return None
        item = results[0]
        name = item["name"] if media_type == "tv" else item["title"]
        or_name = item["original_name"] if media_type == "tv" else item["original_title"]
        img_url = f"https://image.tmdb.org/t/p/original{item['backdrop_path']}"
        overview = item["overview"]
        return name, or_name, img_url, overview
    
    json_data = get_data(imdb_id, "fa")

    # Check TV results first
    tv_results = json_data["tv_results"]
    movie_results = json_data["movie_results"]
    media_type = "tv" if len(tv_results) > 0 else "movie"
    results = tv_results if media_type == "tv" else movie_results

    info = extract_info(results, media_type)
    
    if info and len(info[3]) > 0:
        return info
    else:
        json_data = get_data(imdb_id, "en")
        tv_results = json_data["tv_results"]
        movie_results = json_data["movie_results"]
        media_type = "tv" if len(tv_results) > 0 else "movie"
        results = tv_results if media_type == "tv" else movie_results
        
        return extract_info(results, media_type)

print(infodata("tt0903747"))
