function toggleDarkMode() {
  const body = document.querySelector('body');
  body.classList.toggle('dark-mode');
}

function showCommentForm() {
  
}
$(document).ready(function() {
    $(".comBox").click(function() {
      $(this).siblings(".inter").toggle();
    });
  });