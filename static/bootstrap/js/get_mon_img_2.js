async function get_mon(mon) {
	const ele = document.getElementById("pimg");
	ele.innerHTML = '';
	let response = await fetch('/static/bootstrap/js/pokemon.json');
	const search_dict = await response.json();
	const img = document.createElement("img");
	img.style.maxHeight = "100px";
	img.src = `/static/sprites/pokemon/${search_dict[mon]["img_number"]}.png`;
	ele.appendChild(img);
};