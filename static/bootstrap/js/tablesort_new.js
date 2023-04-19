const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
	v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
	)(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
		const table = th.closest('table');
		const tbody = table.querySelector('tbody');
		const thead = table.querySelector('thead');
		Array.from(tbody.querySelectorAll('tr'))
			.sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
			.forEach(tr => tbody.appendChild(tr) );
		const arrows = thead.querySelectorAll('.arrow');
		for (i=0;i<arrows.length;i++){
			arrows[i].classList.add("fa-sort");
			arrows[i].classList.remove("fa-sort-up");
			arrows[i].classList.remove("fa-sort-down");
		}
		const arrow = th.querySelector('.arrow')
		if (this.asc) {
			arrow.classList.add("fa-sort-up");
			arrow.classList.remove("fa-sort");
		}
		else {
			arrow.classList.add("fa-sort-down");
			arrow.classList.remove("fa-sort");			
		}
	})));
});
