function loadGenes(howMany) {
  var sidebar = document.getElementById("sidebar")
  var length = sidebar.children.length
  var left = length
  var right = howMany + length - 1
  var i = length + 1
  console.log(length)
  console.log(left, right)
  var httpRequest = new XMLHttpRequest()
  httpRequest.onreadystatechange = function(){
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      var geneList = JSON.parse(httpRequest.responseText)
      var numbers = 0
      for (var gene of geneList) {
        var link = document.createElement("a")
        var row = document.createElement("tr")
        var left = document.createElement("th")
        var middle = document.createElement("th")
        var right = document.createElement("th")
        link.setAttribute("href", "#")
        link.setAttribute("data-clusterID", gene[1])
        link.setAttribute("onclick", "var clusterID = this.getAttribute('data-clusterID'); window.parent.geneCanvas$getGeneView(clusterID);")
        if (gene[0].length >= 1) {
          link.innerHTML = gene[0][0]
        } else {
          link.innerHTML = "?"
        }
        left.innerHTML = i + "."
        i += 1
        right.innerHTML = gene[2].toPrecision(2)
        middle.appendChild(link)
        sidebar.appendChild(row)
        row.appendChild(left)
        row.appendChild(middle)
        row.appendChild(right)
        numbers+=1
      }
    }
  }
  httpRequest.open('GET', '/api/geneList/' + left + '/' + right, true)
  httpRequest.send(null);
}

(function(window, document) {
  "use strict"
  window.onload = init
  function init() {
    loadGenes(10)
  }
})(window, document)
