var toolbarOptions = [["bold", "italic"], ["link", "image"], { header: "3" }];
var Delta = Quill.import("delta");

var quill = new Quill("#editor", {
    modules: {
        toolbar: {
            container: "#toolbar", // Selector for toolbar container
        },
    },
    theme: "snow",
});

var saveButton = document.querySelector("#save-button");
saveButton.addEventListener("click", function () {
    console.log("Document saved!");
});

var deleteButton = document.querySelector("#delete-button");
deleteButton.addEventListener("click", function () {
    console.log("Document saved!");
});

// Store accumulated changes
var change = new Delta();
quill.on("text-change", function (delta) {
    change = change.compose(delta);
});

// Save periodically
setInterval(function () {
    if (change.length() > 0) {
        console.log("Saving changes", change);

        // Send entire document
        $.post("/editor/" + post_id + "/update_content", {
            doc: quill.getText(),
        });

        console.log("MESSAGE:");
        console.log("/editor/" + post_id + "/update_content");

        console.log(JSON.stringify(quill.getText()));

        change = new Delta();
    }
}, 5 * 1000);

// Check for unsaved data
window.onbeforeunload = function () {
    if (change.length() > 0) {
        return "There are unsaved changes. Are you sure you want to leave?";
    }
};
