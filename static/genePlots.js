
function addPlot(exonID, plots, sequences, annotation, name) {
  var plotList = []
  for (var i = 0; i < plots.length; i++) {
    plotList.push({"plot": plots[i], "sequence": sequences[i]})
  }
  var plots = document.getElementById("plots")
  var plotRow = document.getElementById("plotRow").innerHTML
  var result = parent.Mustache.render(plotRow, Object.assign(annotation, {exonID: exonID, plots: plotList, name: name}))
  plots.insertAdjacentHTML("beforeend", result)
}

function flip(int) {
  if (int == 1) return 0;
  if (int == 0) return 1;
}

function handleRemove(button) {
  var tr = button.parentElement.parentElement
  try {
    parent.geneCanvas$handleRemovePlot(tr.id)
  } finally {
    removePlots(tr.id)
  }
}

function removePlots(trid) {
  var tr = document.getElementById(trid)
  tr.parentElement.removeChild(tr)
}

function handleHide(button) {
  console.log(button.parent)
  var isHidden = button.getAttribute("data-hidden")
  button.setAttribute("data-hidden", flip(isHidden))
  var children = button.parentElement.parentElement.children;  console.log(children)
  for (var i = 0; i < children.length; i++) {
    var child = children[i]
    if (child.getAttribute("data-containsplot") == 1) {
      if (flip(isHidden)){
        child.setAttribute("hidden", "1")
      }
      else {
        child.removeAttribute("hidden")
      }
    }
  }
  if (flip(isHidden)) {
    button.innerHTML = "Show"
  } else {
    button.innerHTML = "Hide"
  }
}

function plotForProbe(X, Y) {
  var div = document.createElement("div")

  var chartHeight = 200
  var chartWidth = 200

  var data = []

  for (var i = 0; i < X.length; i++) {
    data.push([X[i], Y[i]])
  }

  var margin = {top: 20, right: 15, bottom: 60, left: 60}
  var width = chartHeight - margin.left - margin.right
  var height = chartWidth - margin.top - margin.bottom

  var x = d3.scaleLinear()
    .domain([0, d3.max(data, function(d) { return d[0]; })])
    .range([ 0, width ]);

  var y = d3.scaleLinear()
    .domain([0, d3.max(data, function(d) { return d[1]; })])
    .range([ height, 0 ]);

  var chart = d3.select(div)
  	.append('svg:svg')
  	.attr('width', "100%")
  	.attr('height', chartHeight)
  	.attr('class', 'chart')

  var main = chart.append('g')
  	.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
  	.attr('width', width)
  	.attr('height', height)
  	.attr('class', 'main')

  // draw the x axis
  var xAxis = d3.axisBottom(x)

  main.append('g')
  	.attr('transform', 'translate(0,' + height + ')')
  	.attr('class', 'main axis date')
  	.call(xAxis);

  // draw the y axis
  var yAxis = d3.axisLeft(y)

  main.append('g')
  	.attr('transform', 'translate(0,0)')
  	.attr('class', 'main axis date')
  	.call(yAxis);

  var g = main.append("svg:g");

  //var trend = document.createElementNS("http://www.w3.org/2000/svg", "line");
  var trend = main.append("svg:line");

  trend.attr("x1", x(0))
    .attr("y1", y(0))
    .attr("x2", x(8))
    .attr("y2", y(100))
    .attr("stroke-width", 1)
    .attr("stroke", "black");

    //data = [[0, 1], [2, 3], [4, 5]]
  g.selectAll("scatter-dots")
    .data(data)
    .enter().append("svg:circle")
    .attr("cy", function (d) {return y(d[1])} ) // translate y value to a pixel
    .attr("cx", function (d,i) {return x(d[0])} ) // translate x value
    .attr("r", 2);
  return div.innerHTML
}

function removePlotForExon(exonID) {
  var geneCanvas = window.parent.document.getElementById("genePlots")
  var doc = geneCanvas.contentDocument
  var plots = doc.getElementById("plots")
  var plot = doc.getElementById("plot-" + exonID)
  plots.removeChild(plot)
  while (plot !== undefined) {
    var plot = document.getElementById("plot-" + exonID)
    if (plot !== undefined) {
      plots.removeChild(plot)
    }
  }
}

function handlePlot(exonID){
  var httpRequest = new XMLHttpRequest()
  httpRequest.onreadystatechange = function() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      var d = JSON.parse(httpRequest.responseText)
      console.log(d)
      var probeData = d["probeData"]
      var chipMeta = d["chipMeta"]
      var X = d["modalAllele"]

      var plots = []
      var sequences = []
      //console.log(probeData)
      //console.log(chipMeta)

      for (var metaPiece of chipMeta) {
        var key = metaPiece[0]
        var Y = probeData[key]
        plots.push(plotForProbe(X, Y))
        sequences.push(key)
      }
      console.log(plots)
      addPlot(exonID, plots, sequences, d["annotation"], d["names"].toString())
    }
  }
  httpRequest.open('GET', '/api/plotData/' + exonID, true);
  httpRequest.send(null);
}
