import sites.new_almasmovie
import sites.new_mobomovie
def all_links(name: str, imdbid: str):
    almasmovie_links = sites.new_almasmovie.find_movie_and_links(imdbid)
    mobomovie_links = sites.new_mobomovie.find_movie_and_links(name, imdbid)
    if almasmovie_links is None:
        if mobomovie_links[0] == "movie":
            return "movie", mobomovie_links[1]
        else:
            return "serial", mobomovie_links[1]
    elif mobomovie_links is None:
        return almasmovie_links
    elif mobomovie_links and almasmovie_links:
        dict1 = almasmovie_links[1]
        dict2 = mobomovie_links[1]
        merged_dict = {}
        all_keys = set(dict1.keys()).union(set(dict2.keys()))
        for key in all_keys:
            if key in dict1 and key in dict2:
                merged_dict[key] = {}
                for subkey in set(dict1[key].keys()).union(dict2[key].keys()):
                    if subkey in dict1[key] and subkey in dict2[key]:
                        merged_dict[key][subkey] = {
                            **dict1[key][subkey], **dict2[key][subkey]}
                    elif subkey in dict1[key]:
                        merged_dict[key][subkey] = dict1[key][subkey]
                    elif subkey in dict2[key]:
                        merged_dict[key][subkey] = dict2[key][subkey]
            elif key in dict1:
                merged_dict[key] = dict1[key]
            elif key in dict2:
                merged_dict[key] = dict2[key]
        if mobomovie_links[0] and almasmovie_links[0] =="movie":
            return "movie",merged_dict
        else:
            return "serial",merged_dict
print(all_links("The Godfather","tt0068646"))
