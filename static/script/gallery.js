window.onload = function () {
  var imageContainer = document.getElementById("imageContainer");

  // Array of image filenames
  var images = ["image1.jpg", "image2.jpg", "image3.jpg"];

  // Loop through images array and create HTML elements for each image
  for (var i = 0; i < images.length; i++) {
    var imageDiv = document.createElement("div");
    imageDiv.className = "image";

    var image = document.createElement("img");
    image.src = "images/" + images[i];
    image.onclick = function () {
      enlargeImage(this.src);
    };

    imageDiv.appendChild(image);
    imageContainer.appendChild(imageDiv);
  }

  // Function to enlarge image
  function enlargeImage(src) {
    var modal = document.createElement("div");
    modal.className = "modal";
    modal.onclick = function () {
      closeModal();
    };

    var modalImage = document.createElement("img");
    modalImage.src = src;
    modalImage.className = "modal-image";

    modal.appendChild(modalImage);
    document.body.appendChild(modal);
  }

  // Function to close modal
  function closeModal() {
    var modal = document.getElementsByClassName("modal")[0];
    modal.parentNode.removeChild(modal);
  }
};
