function geneCanvas$getGeneView(clusterID) {
  window.frames["geneCanvas"].contentWindow.getGeneView(clusterID)
}

function genePlots$handleAffyClick(probesetID){
  window.frames["genePlots"].contentWindow.plot(probesetID)
}
