window.addEventListener('load', function() {
    const loader = document.getElementById('loader');
    loader.classList.add('hidden');
});

// show table(s)
$('table.display').DataTable({"pageLength": -1});

// get scores
function getScores() {
    // get form data
    var formData = $('#selected-rows-form').serialize();

    // send ajax request
    $.ajax({
        type: 'POST',
        url: '/get_differences',
        data: formData,
        success: function(response) {
            // show header
            var brElement = $('<br></br>');
            var h3Element = $('<h3>Differences:</h3>');
            $('#differences-results').empty();
            $('#differences-results').append(h3Element);
            // show table
            $('#differences-results').append('<div class="table-wrapper">' + response.df_html_output + '</div>');
            // download as csv link
            $('#differences-results').append('<a href="/download_csv/df_html_differences" class="download-link">Download as CSV</a>');
        },
        error: function(error) {
            console.error('Error:', error)
        }
    });
}