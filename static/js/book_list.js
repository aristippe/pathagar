$(document).ready(function () {
    $('#book_list').DataTable({
        paging: false,
        searching: false,
        ordering: false,
        select: true,
        bInfo: false
    });

    $('#author_list').DataTable({
        paging: false,
        searching: false,
        ordering: false,
        select: true,
        bInfo: false
    });

    $('#book_list tbody, #author_list tbody').on('click', 'tr', function () {
        $(this).toggleClass('selected');
    });

    $('#button').click(function () {
        alert(table.rows('.selected').data().length + ' row(s) selected');
    });

    $('#book_list').
      on('mouseover', 'tr', function() {
          $(this).find('.download').show();
      }).
      on('mouseout', 'tr', function() {
          $(this).find('.download').hide();
      });

    $('#author_list').
      on('mouseover', 'tr', function() {
          $(this).find('.download').show();
      }).
      on('mouseout', 'tr', function() {
          $(this).find('.download').hide();
      });

});
