function geneCanvas$getGeneView(clusterID) {
  window.frames["geneCanvas"].contentWindow.getGeneView(clusterID)
}

function genePlots$handleAffySelect(probesetID) {
  window.frames["genePlots"].contentWindow.handlePlot(probesetID)
}

function genePlots$handleAffyDeselect(affyID) {
  window.frames["genePlots"].contentWindow.removePlots("affy-" + affyID)
}

function geneCanvas$handleRemovePlot(affyID) {
  window.frames["geneCanvas"].contentWindow.handleRemovePlot(affyID)
}
