// Getting elements for mobile view
const sidebar = document.querySelector('.sidebar');
const close = document.getElementById('close');
const menu = document.getElementById('menu');

// Add event listener, for when the button is clicked
close.addEventListener('click', hideSidebar);
menu.addEventListener('click', showSidebar);

// For mobile views
function showSidebar(){
  sidebar.style.display = 'flex'
}
function hideSidebar(){
  sidebar.style.display = 'none'
}