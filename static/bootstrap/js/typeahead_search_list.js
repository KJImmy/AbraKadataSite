// import search_list from './search_list.json' assert {type: 'json'};

$(document).ready(async function(){
    // Defining the local dataset
    var searchable = ['Audi', 'BMW', 'Bugatti', 'Ferrari', 'Ford', 'Lamborghini', 'Mercedes Benz', 'Porsche', 'Rolls-Royce', 'Volkswagen'];
    
    let response = await fetch('/static/bootstrap/js/search_list.json');
    
    // let search_list = require('./search_list.json');

    var searchable = await response.json();

    // Constructing the suggestion engine
    var searchable = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        local: searchable
    });
    
    // Initializing the typeahead
    $('.typeahead').typeahead({
        hint: true,
        highlight: true, /* Enable substring highlighting */
        minLength: 1 /* Specify minimum characters required for showing suggestions */
    },
    {
        name: 'searchable',
        source: searchable
    });
});