var toolbarOptions = [["bold", "italic"], ["link", "image"], { header: "3" }];

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
