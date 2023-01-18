// import search_dict from './search_dict.json' assert {type: 'json'};

// {% url 'format_pokemon' tier.generation tier.tier_name t.pokemon_unique_name %}

const submitbtn = document.getElementById("submitbtn");

searchRedirect = async function(event) {
    console.log("running redirect");
    event.preventDefault();
	let response = await fetch('/static/bootstrap/js/search_dict.json');
	const search_dict = await response.json();
    console.log("successfully retrieved search json")
	const search = document.getElementById("search_form");
    const search_text = document.getElementById("search_input");
    if (!(search_text.value in search_dict)) {
    	console.log("returning false")
    	return false;
    }
    const redirect_string = `/formats/gen${search_dict[search_text.value][1]}${search_dict[search_text.value][2]}/${search_dict[search_text.value][0]}`
    search.action = redirect_string;
    search.submit();
    console.log("redirecting");
    console.log(search_text.value);
    console.log(redirect_string);
    console.log(search);
    // return this.http.get(url,{responseType: 'text'});
}

submitbtn.addEventListener('click',searchRedirect);