var exon1 = [10, 20]
var exon2 = [35, 45]
var exon3 = [55, 60]

var exons = [exon1, exon2, exon3]
exonID = ["a", "b", "c"]

var exons2 = [[20, 30], [50, 70], [100, 150]]

var heightC = 20
var trackSpace = 30
var topC = 10

var unselectedOpc = 0.6

function trackLocation(track) {
  return (heightC + trackSpace) * track
}

var busyIDs = []

function getPlotID() {
  index = busyIDs.findIndex(function(elem){if (elem == 0) return true})
  if (index == -1) {
    busyIDs.push(1)
    return busyIDs.length - 1
  } else {
    busyIDs[index] = 1
    return index
  }
}

function plotForExon(exonID) {
  
}

function releasePlotID(index) {
  busyIDs[index] = 0
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
  console.log("TODO", exonRect.innerHTML)
}

function flipSelection(exonRect) {
  isSelected = exonRect.getAttributeNS(null, "data-selected")
  //console.log(exonRect.getAttributeNS(null, "data-exonID"))
  if (isSelected == 1) {
    deselectExon(exonRect)
  } else {
    selectExon(exonRect)
  }
}

function handleExonClick(evt) {
  var svgobj=evt.target
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

  var rightLine = document.createElementNS("http://www.w3.org/2000/svg", "line")
  rightLine.setAttributeNS(null, "x1", right)
  rightLine.setAttributeNS(null, "x2", midX)
  rightLine.setAttributeNS(null, "y1", midY)
  rightLine.setAttributeNS(null, "y2", bottomY)
  rightLine.setAttributeNS(null, "stroke", "#74AD68")

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

// code that should be taken care of right away

window.onload = init;

  function init() {
    drawExons(exons, exonID, "CFH", 0)
    drawExons(exons2, exonID, "CFHR-1", 1)
  }

})(window, document, undefined);
