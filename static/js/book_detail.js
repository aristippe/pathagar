$(document).ready(function () {


    $('#delete').click(function (event) {
        if (confirm('Are you sure you want to delete this?')) {
            $.ajax({
                url: '{{book_delete }} book.pk',
                type: "POST",
                data: {
                    // data stuff here
                },
                success: function () {
                    // does some stuff here...
                }
            });
        }
    });

});
