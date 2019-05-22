/* Create an instance of CSInterface. */
var csInterface = new CSInterface();
/* Make a reference to your HTML button and add a click handler. */
var openButton = document.querySelector("#tikManager-button");
openButton.addEventListener("click", tikUI);
var versionButton = document.querySelector("#version-button");
versionButton.addEventListener("click", saveAsVersion);
/* Write a helper function to pass instructions to the ExtendScript side. */
function tikUI() {
  csInterface.evalScript("tikUI()");
}
function saveAsVersion() {
  csInterface.evalScript("saveAsVersion()");
}