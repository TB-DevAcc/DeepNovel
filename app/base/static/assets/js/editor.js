var quill = new Quill("#editor", {
    modules: {
        toolbar: {
            container: "#toolbar", // Selector for toolbar container
        },
        history: {
            delay: 2000,
            maxStack: 500,
            userOnly: true,
        },
    },
    theme: "snow",
});

var Delta = Quill.import("delta");

// Store accumulated changes
var change = new Delta();
quill.on("text-change", function (delta) {
    change = change.compose(delta);
});

// Save periodically
setInterval(function () {
    if (change.length() > 0) {
        console.log("Saving changes ", change);

        // Send entire document
        $.post("/editor/" + post_id + "/update_content", {
            doc: $("#editor").find(".ql-editor").html(),
        });

        change = new Delta();
    }
}, 5 * 1000);

// Check for unsaved data
window.onbeforeunload = function () {
    if (change.length() > 0) {
        return "There are unsaved changes. Are you sure you want to leave?";
    }
};

// AI

function generate() {
    // Ask server for generation
    $.post("/generate/" + post_id, { doc: quill.getText(), length: 1 }, function (data) {
        var s = quill.getSelection().index || 0;
        quill.insertText(s, data, "user");
        quill.setSelection(quill.getLength(), 0, "user");
    });
}

// Text generation on tab press
$("body").keydown(function (e) {
    var code = e.key || e.which;

    if (code === 9 || code === "Tab") {
        e.preventDefault();
        generate();
    }
});

// Question answering
$(function () {
    $("#main-search-form").submit(function (event) {
        event.preventDefault();
        console.log("LOGGING QUESTION", document.getElementById("#main-search-form").question);
        $.get("/answer/" + post_id + "/" + $(this).question, function (data) {
            console.log(data);
        });
    });
});

// Buttons

$("#btn-generate-1").click(function () {
    $("#btn-generate-1").replaceWith(
        "<div id='btn-generate-1' class='spinner-grow text-warning'></div>"
    );

    function generate_length() {
        // Ask server for generation
        $.post("/generate/" + post_id, { doc: quill.getText(), length: 1 }, function (data) {
            var s = quill.getSelection().index || 0;
            quill.insertText(s, data, "user");
            quill.setSelection(quill.getLength(), 0, "user");
            $("#btn-generate-1").replaceWith(
                "<button id='btn-generate-1' type='button' class='btn my-2 btn-fw'>Line</button>"
            );
        });
    }
    generate_length();
});

$("#btn-generate-2").click(function () {
    $("#btn-generate-2").replaceWith(
        "<div id='btn-generate-2' class='spinner-grow text-warning'></div>"
    );

    function generate_length() {
        // Ask server for generation
        $.post("/generate/" + post_id, { doc: quill.getText(), length: 40 }, function (data) {
            var s = quill.getSelection().index || 0;
            quill.insertText(s, data, "user");
            quill.setSelection(quill.getLength(), 0, "user");
            $("#btn-generate-2").replaceWith(
                "<button id='btn-generate-2' type='button' class='btn my-2 btn-fw'>Paragraph</button>"
            );
        });
    }
    generate_length();
});

$("#btn-generate-3").click(function () {
    $("#btn-generate-3").replaceWith(
        "<div id='btn-generate-3' class='spinner-grow text-warning'></div>"
    );

    function generate_length() {
        // Ask server for generation
        $.post("/generate/" + post_id, { doc: quill.getText(), length: 4000 }, function (data) {
            var s = quill.getSelection().index || 0;
            quill.insertText(s, data, "user");
            quill.setSelection(quill.getLength(), 0, "user");
            $("#btn-generate-3").replaceWith(
                "<button id='btn-generate-3' type='button' class='btn my-2 btn-fw'>Chapter</button>"
            );
        });
    }
    generate_length();
});
