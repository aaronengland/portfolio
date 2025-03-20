window.addEventListener('load', function() {
    const loader = document.getElementById('loader');
    loader.classList.add('hidden');
});

// show tables
$('table.display').DataTable({
    searching: true,
    lengthChange: true,
    paging: true,
    info: true,
});