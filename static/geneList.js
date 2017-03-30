function loadGenes() {
  var i = 1
  var sidebar = document.getElementById("sidebar")
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
        link.setAttribute("onclick", "window.parent.geneCanvas$getGeneView(this.getAttribute('data-clusterID'))")
        if (gene[0].length >= 1) {
          link.innerHTML = gene[0][0]
        } else {
          link.innerHTML = "?"
        }
        left.innerHTML = i + "."
        i += 1
        right.innerHTML = gene[2].toPrecision(2)
        link.setAttributeNS(null, "data-clusterID", gene[1])
        middle.appendChild(link)
        sidebar.appendChild(row)
        row.appendChild(left)
        row.appendChild(middle)
        row.appendChild(right)
        numbers+=1
      }
    }
  }
  httpRequest.open('GET', '/api/geneList', true);
  httpRequest.send(null);
}

(function(window, document) {
  "use strict"
  window.onload = init
  function init() {
    loadGenes()
  }
})(window, document)
