$(document).ready(function () {
    $('#book_list').DataTable({
        paging: false,
        searching: false,
        ordering: false,
        select: true
    });

    $('#book_list tbody').on('click', 'tr', function () {
        $(this).toggleClass('selected');
    });

    $('#button').click(function () {
        alert(table.rows('.selected').data().length + ' row(s) selected');
    });

});
