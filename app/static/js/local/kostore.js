    // some variables
    //var url = "https://www.googleapis.com/books/v1/volumes?q=the+Cat+In+The+Hat";
    var url = "/kostore/tester/";
    var url2 = "/kostore/tester/";

    var viewModel = {};

$(document).ready(function () {
    //Knockout Test

    $.getJSON(url, function (data) {
        console.log(data);
        viewModel.model = ko.mapping.fromJS(data);
        ko.applyBindings(viewModel);
    });


    $('#btnTest').click(function () {
        $.getJSON(url2, function (data) {
            console.log(data);
            ko.mapping.fromJS(data, viewModel.model);
        });
    });
});
