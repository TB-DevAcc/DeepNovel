// Import React dependencies.
import React, { useEffect, useMemo, useState } from "react";
// Import the Slate editor factory.
import { createEditor } from "slate";

// Import the Slate components and React plugin.
import { Slate, Editable, withReact } from "slate-react";

// Define our app...
const App = () => {
    // Create a Slate editor object that won't change across renders.
    const editor = useMemo(() => withReact(createEditor()), []);
    // Keep track of state for the value of the editor.
    // Add the initial value when setting up our state.
    const [value, setValue] = useState([
        {
            type: "paragraph",
            children: [{ text: "A line of text in a paragraph." }],
        },
    ]);
    // Render the Slate context.
    return (
        // Add the editable component inside the context.
        <Slate editor={editor} value={value} onChange={(newValue) => setValue(newValue)}>
            <Editable />
        </Slate>
    );
};

const domContainer = document.querySelector("#editor-wrapper");
ReactDOM.render(e(App), domContainer);
