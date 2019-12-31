$(document).ready(function () {
  // Check for click events on the navbar burger icon
  $(".navbar-burger").click(function () {
    // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
    $(".navbar-burger").toggleClass("is-active");
    $(".navbar-menu").toggleClass("is-active");
  });
});

document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'delete') {
      element.parentElement.style.animationPlayState = 'running';
      element.parentElement.addEventListener('animationend', () => {
        element.parentElement.remove();
      });
    }
  });
});