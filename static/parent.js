
function getFrame(frameName) {
  var chromeFrame = window.frames[frameName].contentWindow
  if (chromeFrame === undefined) {
    var safariFrame = window.frames[frameName].window
    return safariFrame
  }
  return chromeFrame
}

function geneCanvas$getGeneView(clusterID) {
  getFrame("geneCanvas").getGeneView(clusterID)
}

function genePlots$handleAffySelect(probesetID) {
  getFrame("genePlots").handlePlot(probesetID)
}

function genePlots$handleAffyDeselect(affyID) {
  getFrame("genePlots").removePlots("affy-" + affyID)
}

function geneCanvas$handleRemovePlot(affyID) {
  getFrame("geneCanvas").handleRemovePlot(affyID)
}

function geneCanvas$handleFlickerPlot(affyID) {
  getFrame("geneCanvas").handleFlickerPlot(affyID)
}
