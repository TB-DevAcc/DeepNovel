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
    $.get("/generate/" + post_id, function (data) {
        quill.insertText(quill.getSelection().index, data, "user");
        quill.setSelection(quill.getLength(), 0, "user");
    });
}

// Text generation on button press
$("#generate-button").click(function () {
    generate();
});

// Text generation on tab press
$("body").keydown(function (e) {
    var code = e.keyCode || e.which;

    if (code === 9) {
        e.preventDefault();
        generate();
    }
});
