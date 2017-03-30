var exon1 = [10, 20]
var exon2 = [35, 45]
var exon3 = [55, 60]

var exons = [exon1, exon2, exon3]
exonID = ["a", "b", "c"]

var exons2 = [[20, 30], [50, 70], [100, 150]]


var selectedIDs = []

function getPlotID(id) {
  index = selectedIDs.findIndex(function(elem){if (elem == 0) return true})
  if (index == -1) {
    selectedIDs.push(id)
    return selectedIDs.length - 1
  } else {
    selectedIDs[index] = id
    return index
  }
}

function releasePlotID(index) {
  selectedIDs[index] = 0
}

var dataX = [0, 1, 2, 3, 4, 5, 6, 7, 8]

var dataForExon = {
  "a" : [10, 70, 150, 320, 11, 88, 154, 321, 100],
  "b" : [10, 20, 110, 70, 30, 18, 75, 121, 4],
  "c" : [3, 390, 160, 2, 118, 153, 100, 1, 227]
}

function removePlotForExon(exonID) {
  var geneCanvas = window.parent.document.getElementById("genePlots")
  var doc = geneCanvas.contentDocument
  var plots = doc.getElementById("plots")
  var plot = doc.getElementById("plot-" + exonID)
  plots.removeChild(plot)
  while (plot !== undefined) {
    plot = document.getElementById("plot-" + exonID)
    if (plot !== undefined) {
      plots.removeChild(plot)
    }
  }
}

function chooseGene(evt) {
  console.log(evt.target.value)

}

function handleRemove() {
  var geneCanvas = window.parent.document.getElementById("genePlots")
  geneCanvas.contentWindow.clickedButton.parentElement.parentElement.remove()
}

function containerForExonPlot(exonID) {
  var geneCanvas = window.parent.document.getElementById("genePlots")
  var doc = geneCanvas.contentDocument
  console.log(doc)
  var plots = doc.getElementById("plots")
  console.log(plots)
  var exPlotID = "plot-" + exonID
  container = document.createElementNS(null, "tr")
  container.setAttribute("border", 1)

  outerButton = document.createElementNS(null, "th")
  button = document.createElement("button")
  button.innerHTML = "Remove"
  outerButton.appendChild(button)
  container.appendChild(outerButton)
  var clickedButton
  button.setAttribute("onclick", "this.parentElement.parentElement.remove()")
  container.id = exPlotID
  plots.appendChild(container)
  return container
}

function plotForExon(container, X, Y) {

  div = document.createElement("th")
  container.appendChild(div)

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
  	.attr('width', chartWidth)
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

}
