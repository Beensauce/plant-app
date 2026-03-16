const modal = document.getElementById('modal-overlay');
const btn = document.getElementById('add-plant-btn');
const closeBtn = document.getElementById('close-modal');

// Open modal
btn.addEventListener('click', function () {
    modal.style.display = 'flex';
});

// Close modal via X button
closeBtn.addEventListener('click', function () {
    modal.style.display = 'none';
});

  // Close modal by clicking outside content
  window.addEventListener('click', function (event) {
      if (event.target === modal) {
          modal.style.display = 'none';
      }
  });