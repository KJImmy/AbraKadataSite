function sortTable(n,t,numbers=false) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("sortable"+t);
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc";
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 1; i < (rows.length - 1); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      if (numbers) {
        if (dir == "asc") {
          if (x.innerText.toLowerCase() < y.innerText.toLowerCase()) {
            //if so, mark as a switch and break the loop:
            shouldSwitch= true;
            break;
          }
        } else if (dir == "desc") {
          if (x.innerText.toLowerCase() > y.innerText.toLowerCase()) {
            //if so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        }
      }
      else {
        if (dir == "asc") {
          if (x.innerText.toLowerCase() > y.innerText.toLowerCase()) {
            console.log("inner x is: "+x.innerText,"inner y is: "+y.innerText,x.innerText>y.innerText)
            //if so, mark as a switch and break the loop:
            shouldSwitch= true;
            break;
          }
        } else if (dir == "desc") {
          if (x.innerText.toLowerCase() < y.innerText.toLowerCase()) {
            //if so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch
      and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++;      
    } else {
      /*If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
  columns = table.rows[0].cells.length;
  for (i = 0; i < columns; i++) {
    arrow = document.getElementById("arrow"+t+i);
    if (arrow) {
      arrow.classList.add("fa-sort");
      arrow.classList.remove("fa-sort-up");
      arrow.classList.remove("fa-sort-down");
    }
  }
  if (numbers) {
    if (dir == "desc") {
      arrow = document.getElementById("arrow"+t+n);
      arrow.classList.add("fa-sort-up");
      arrow.classList.remove("fa-sort");
      arrow.classList.remove("fa-sort-down");
    }
    else if (dir == "asc") {
      arrow = document.getElementById("arrow"+t+n);
      arrow.classList.add("fa-sort-down");
      arrow.classList.remove("fa-sort");
      arrow.classList.remove("fa-sort-up");
    }
  } else {
    if (dir == "asc") {
      arrow = document.getElementById("arrow"+t+n);
      arrow.classList.add("fa-sort-up");
      arrow.classList.remove("fa-sort");
      arrow.classList.remove("fa-sort-down");
    }
    else if (dir == "desc") {
      arrow = document.getElementById("arrow"+t+n);
      arrow.classList.add("fa-sort-down");
      arrow.classList.remove("fa-sort");
      arrow.classList.remove("fa-sort-up");
    }
  }
}