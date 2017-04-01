function containerForExonPlot(exonID) {
  var plots = document.getElementById("plots")
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
  div = document.createElement( "th")
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

function plot(exonID){
  var httpRequest = new XMLHttpRequest()
  httpRequest.onreadystatechange = function() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      var d = JSON.parse(httpRequest.responseText)
      var container = containerForExonPlot(exonID)
      console.log(d)
      probeData = d["probeData"]
      for (var key in probeData) {
        if (probeData.hasOwnProperty(key)) {
          var Y = probeData[key]
          var X = d["modalAllele"]
          plotForExon(container, X, Y)
        }
      }
    }
  }
  httpRequest.open('GET', '/api/plotData/' + exonID, true);
  httpRequest.send(null);
}
