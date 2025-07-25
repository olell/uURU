function updateTheme() {
  const colorMode = window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
  document.querySelector("html").setAttribute("data-bs-theme", colorMode);
}
updateTheme();
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", updateTheme);

$(document).ready(() => {
  // show the alert
  setTimeout(() => {
    $(".alert").alert("close");
  }, 2000);
});
