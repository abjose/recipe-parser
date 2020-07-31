function myFunction() {
  var x = document.getElementById("pasted-recipe").value;
  document.getElementById("demo").innerHTML = x;
}

document.addEventListener("DOMContentLoaded", function(event) { 
  document.getElementById("parse-button").onclick = myFunction;  
});

