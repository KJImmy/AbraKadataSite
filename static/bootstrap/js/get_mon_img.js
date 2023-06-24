async function get_(mon) {
	const ele = document.getElementById("pimg");
	ele.innerHTML = '';
	let response = await fetch('/static/bootstrap/js/pokemon.json');
	const search_dict = await response.json();
	const img = document.createElement("img");
	console.log("working");
	console.log(search_dict[mon]);
	img.src = `/static/sprites/pokemon/${search_dict[mon]["img_number"]}.png`;
	ele.appendChild(img);
};