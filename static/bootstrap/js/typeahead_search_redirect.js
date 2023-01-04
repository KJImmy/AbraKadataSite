// import search_dict from './search_dict.json' assert {type: 'json'};

// {% url 'format_pokemon' tier.generation tier.tier_name t.pokemon_unique_name %}

window.searchRedirect = function() {
	let search_dict = await fetch('./search_dict.json')
	const search = document.getElementById("search_form")
    const search_text = document.getElementById("search_input");
    if (!(search_text.value in search_dict)) {
    	return false;
    }
    const redirect_string = `/formats/gen${search_dict[search_text.value][1]}${search_dict[search_text.value][2]}/${search_dict[search_text.value][0]}`
    search.action = redirect_string;
    // return this.http.get(url,{responseType: 'text'});
}