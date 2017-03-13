var exon1 = [10, 20]
var exon2 = [35, 45]
var exon3 = [55, 60]

var exons = [exon1, exon2, exon3]
exonID = ["a", "b", "c"]

var exons2 = [[20, 30], [50, 70], [100, 150]]

var heightC = 20
var trackSpace = 30
var topC = 10

var chartHeight = 200
var chartWidth = 200

var unselectedOpc = 0.6

function trackLocation(track) {
  return (heightC + trackSpace) * track
}

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

function plotForExon(exonID) {
  var plots = document.getElementById("body")

  var plotID = getPlotID()
  var exPlotID = "plot-" + plotID

  div = document.createElementNS(null, "div")
  div.id = exPlotID

  plots.appendChild(div)

  var data = [[5,3], [10,17], [15,4], [2,8]];



  var X = dataX

  var Y = dataForExon[exonID]


  var margin = {top: 20, right: 15, bottom: 60, left: 60}
    , width = chartHeight - margin.left - margin.right
    , height = chartWidth - margin.top - margin.bottom;

      var x = d3.scaleLinear()
                .domain([0, d3.max(data, function(d) { return d[0]; })])
                .range([ 0, width ]);

      var y = d3.scaleLinear()
      	      .domain([0, d3.max(data, function(d) { return d[1]; })])
      	      .range([ height, 0 ]);

    var chart = d3.select(div)
  	.append('svg:svg')
  	.attr('width', width + margin.right + margin.left)
  	.attr('height', height + margin.top + margin.bottom)
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

      g.selectAll("scatter-dots")
        .data([X, Y])
        .enter().append("svg:circle")
            .attr("cx", function(d, i) {console.log(d); return d[0][i]} )
            .attr("cy", function (d) { return y(d[1]); } )
            .attr("r", 2);




}

function createExonRect(left, right, track, exonID) {
  var exonRect = document.createElementNS("http://www.w3.org/2000/svg", "rect")
  exonRect.setAttributeNS(null, "x", left)
  exonRect.setAttributeNS(null, "y", topC + trackLocation(track))
  exonRect.setAttributeNS(null, "width", right - left)
  exonRect.setAttributeNS(null, "height", heightC)
  exonRect.setAttributeNS(null, "fill", "#74AD68")
  exonRect.setAttributeNS(null, "fill-opacity", unselectedOpc)
  exonRect.setAttributeNS(null, "onclick", "onExonClick(evt)")
  exonRect.setAttributeNS(null, "height", heightC)
  exonRect.setAttributeNS(null, "data-selected", 0)
  exonRect.setAttributeNS(null, "data-exonID", exonID)
  return exonRect
}

function deselectExon(exonRect) {
  exonRect.removeAttributeNS(null, "stroke")
  exonRect.removeAttributeNS(null, "stroke-width")
  exonRect.setAttributeNS(null, "fill-opacity", unselectedOpc)
  exonRect.setAttributeNS(null, "data-selected", 0)
  releasePlotID(exonRect.innerHTML)
  console.log("TODO", exonRect.innerHTML)
  exonRect.innerHTML = ""
}

function selectExon(exonRect) {
  exonRect.setAttributeNS(null, "stroke", "black")
  exonRect.setAttributeNS(null, "stroke-width", "1")
  exonRect.setAttributeNS(null, "fill-opacity", "1")
  exonRect.setAttributeNS(null, "data-selected", 1)
  exonRect.setAttributeNS(null, "font-family", "monospace")
  exonRect.innerHTML = getPlotID()
  exonID = exonRect.getAttributeNS(null, "data-exonID")
  plotForExon(exonID)
  console.log("TODO", exonRect.innerHTML)
}

function flipSelection(exonRect) {
  isSelected = exonRect.getAttributeNS(null, "data-selected")
  if (isSelected == 1) {
    deselectExon(exonRect)
  } else {
    selectExon(exonRect)
  }
}

function handleExonClick(evt) {
  var svgobj = evt.target
  flipSelection(svgobj)
}

function createConnector(left, right, track) {
  var trackOffset = trackLocation(track)

  var midX = (right + left)/2
  var midY = topC + heightC/2 + trackOffset
  var bottomY = topC + heightC + trackOffset

  var leftLine = document.createElementNS("http://www.w3.org/2000/svg", "line")
  leftLine.setAttributeNS(null, "x1", left)
  leftLine.setAttributeNS(null, "x2", midX)
  leftLine.setAttributeNS(null, "y1", midY)
  leftLine.setAttributeNS(null, "y2", bottomY)
  leftLine.setAttributeNS(null, "stroke", "#74AD68")
  leftLine.setAttributeNS(null, "stroke-opacity", unselectedOpc)

  var rightLine = document.createElementNS("http://www.w3.org/2000/svg", "line")
  rightLine.setAttributeNS(null, "x1", right)
  rightLine.setAttributeNS(null, "x2", midX)
  rightLine.setAttributeNS(null, "y1", midY)
  rightLine.setAttributeNS(null, "y2", bottomY)
  rightLine.setAttributeNS(null, "stroke", "#74AD68")
  rightLine.setAttributeNS(null, "strok-opacity", unselectedOpc)


  return [leftLine, rightLine]
}

function drawExons(exons, ids, description, track) {
  var canvas = document.getElementById("geneCanvas")

  for (var i = 0; i < exons.length - 1; i++) {
    var right = exons[i][1]
    var left = exons[i + 1][0]
    for (var c of createConnector(left, right, track)) {
      canvas.appendChild(c)
    }
  }

  for (var i = 0; i < exons.length; i++) {
    canvas.appendChild(createExonRect(exons[i][0], exons[i][1], track, ids[i]))
  }

  if (exons.length != 0) {
    x = exons[0][0]
    y = trackLocation(track + 1)
    text = document.createElementNS("http://www.w3.org/2000/svg", "text")
    text.setAttributeNS(null, "x", x)
    text.setAttributeNS(null, "y", y)
    text.setAttributeNS(null, "font-family", "monospace")
    text.innerHTML = description
    canvas.appendChild(text)
  }
}

(function(window, document, undefined) {
"use strict"

window.onload = init;

  function init() {
    drawExons(exons, exonID, "CFH", 0)
    drawExons(exons2, exonID, "CFHR-1", 1)
  }

})(window, document, undefined);
