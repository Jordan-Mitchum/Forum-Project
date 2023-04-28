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
  
  
let likes = 0;
$(document).ready(function () {
   likes = 0;
   setLikes(likes);
});
      
$("body").on("click", ".likeBtn", function () {
   likes++;
   setLikes(likes);
});

function setLikes(count) {
   $(this).children(".totalLikes").text(count);
}