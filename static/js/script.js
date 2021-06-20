
function sendMail(reviewForm) {
  emailjs.send("sami", "ms3-project", {
      "from_name": reviewForm.name.value,
      "from_email": reviewForm.email.value,
      "request_message": reviewForm.message.value,
  })
      .then(
          function () {
              let sentButton = document.getElementById('send-btn');
              sentButton.style.backgroundColor = "brown";
              sentButton.innerHTML = "Review Sent";
          },
          function (error) {
              alert("Ups, there's a problem! Please try submiting the review again! Thanks :)", error);
          });
          document.getElementById('reviewForm').reset();
  return false;
}