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
        var s = quill.getSelection() ? quill.getSelection().index : 0;
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
        console.log("LOGGING QUESTION", document.getElementById("main-search-field").value);
        var question = document.getElementById("main-search-field").value;

        // start modal
        $("#answer-modal").modal("show");
        $("#answer-loader").show();
        $("#generated-answer").text("");
        $("#answer-modal-title").text(question);

        // send request
        $.post("/answer/" + post_id, { question: question, doc: quill.getText() }, function (
            data
        ) {
            console.log(data["answer"]);
            $("#answer-loader").hide();
            $("#generated-answer").text(data["answer"]);
            $("#main-search-field").val("");
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
            var s = quill.getSelection() ? quill.getSelection().index : 0;
            quill.insertText(s, data, "user");
            quill.setSelection(quill.getLength(), 0, "user");
            $("#btn-generate-1").replaceWith(
                "<button id='btn-generate-1' type='button' class='btn btn-generate my-2 btn-fw'>Line</button>"
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
            var s = quill.getSelection() ? quill.getSelection().index : 0;
            quill.insertText(s, data, "user");
            quill.setSelection(quill.getLength(), 0, "user");
            $("#btn-generate-2").replaceWith(
                "<button id='btn-generate-2' type='button' class='btn btn-generate my-2 btn-fw'>Paragraph</button>"
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
            var s = quill.getSelection() ? quill.getSelection().index : 0;
            quill.insertText(s, data, "user");
            quill.setSelection(quill.getLength(), 0, "user");
            $("#btn-generate-3").replaceWith(
                "<button id='btn-generate-3' type='button' class='btn btn-generate my-2 btn-fw'>Chapter</button>"
            );
        });
    }
    generate_length();
});

// Analysis

function getIndicesOf(searchStr, str, caseSensitive) {
    var startIndex = 0,
        index,
        indices = [];
    if (!caseSensitive) {
        str = str.toLowerCase();
        searchStr = searchStr.toLowerCase();
    }
    while ((index = searchStr.indexOf(str, startIndex)) > -1) {
        indices.push(index);
        startIndex = index + 1;
    }
    return indices;
}

function customGetText() {
    return quill
        .getContents()
        .filter(function (op) {
            return typeof op.insert === "string" || op.insert.image;
        })
        .map(function (op) {
            if (op.insert.image) {
                return (op.insert.image = "i");
            }
            return op.insert;
        })
        .join("");
}

function find_replace(word, color) {
    let totalText = customGetText();
    let re = new RegExp(word, "g");
    // make sure the text contains the word I want.
    let match = re.test(totalText);
    if (match) {
        let indices = getIndicesOf(totalText, word, true);
        let length = word.length;

        // apply style..
        console.log("Marking", word, color, "at", indices, length);
        indices.forEach((index) => quill.formatText(index, length, { color: color }, true));
    }
}

$("#btn-analyze").click(function () {
    $("#btn-analyze").replaceWith("<div id='btn-analyze' class='spinner-grow text-info'></div>");
    //$(".loader-wrapper").fadeIn("slow");
    // Ask server for generation
    $.post("/analyze/" + post_id, { doc: quill.getText() }, function (data) {
        console.log(data);
        // Mark People
        var i;
        for (i = 0; i < data["P"].length; i++) {
            console.log("Marking people");
            find_replace(data["P"][i], "rgb(255, 0, 0)");
        }
        // Mark Organizations
        var i;
        for (i = 0; i < data["O"].length; i++) {
            console.log("Marking organizations");
            find_replace(data["O"][i], "rgb(0, 0, 255)");
        }
        // Mark Locations
        var i;
        for (i = 0; i < data["L"].length; i++) {
            console.log("Marking locations");
            find_replace(data["L"][i], "rgb(0, 255, 0)");
        }

        // reset
        $("#btn-analyze").replaceWith(
            '<button id="btn-analyze" type="button" class="btn btn-analyze my-2 btn-fw">Analyze</button>'
        );
        //$(".loader-wrapper").fadeOut("slow");
    });
});

// Reset Colors
$("#btn-reset-colors").click(function () {
    console.log("RESET COLORS");
    quill.formatText(0, quill.getLength(), { color: "rgb(0, 0, 0)" });
});
