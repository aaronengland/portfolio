$(document).ready(function() {
    $('table.display').DataTable();
});


// Event listener for window resize
window.addEventListener('resize', function() {
    resizePlot_1();
    resizePlot_2();
    resizePlot_3();
    resizePlot_4();
    resizePlot_5();
    resizePlot_6();
    resizePlot_7();
});
// Initial resizing of the plot on page load
window.addEventListener('load', function() {
    resizePlot_1();
    resizePlot_2();
    resizePlot_3();
    resizePlot_4();
    resizePlot_5();
    resizePlot_6();
    resizePlot_7();
}); 