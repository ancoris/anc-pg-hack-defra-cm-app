import React, { useState } from "react";
import styles from "./TextGen.module.css";
import { getFunctions, httpsCallable } from "firebase/functions";
import { marked } from "marked";
import { getStorage, ref, uploadBytes, getDownloadURL } from "firebase/storage";

const DEFAULT_CONTENT_TYPE =
    "gs://anc-pg-hack-defra-cm.appspot.com/content_type_policies_example - detailed guide.pdf";

function TextGen() {
    const [inputText, setInputText] = useState("");
    const [outputText, setOutputText] = useState("");
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [promptUsed, setPromptUsed] = useState(""); //unused for now
    const [contentType, setContentType] = useState(DEFAULT_CONTENT_TYPE);
    const [taxonomy, setTaxonomy] = useState("");

    const functions = getFunctions();
    const storage = getStorage();

    const bucketName = "uploaded_docs";

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        try {
            let fileUrl = "";
            if (!selectedFile) {
                alert("Please select a file to upload");
                setLoading(false);
                return;
            }
            if (selectedFile) {
                const storageRef = ref(
                    storage,
                    `${bucketName}/${selectedFile.name}`
                );
                await uploadBytes(storageRef, selectedFile);
                fileUrl = await getDownloadURL(storageRef);
            }

            const generateDocuments = httpsCallable(
                functions,
                "generateDocuments"
            );

            generateDocuments({
                request: inputText,
                fileUrl: fileUrl,
                contentType: contentType,
            }).then((result) => {
                console.log(result.data);
                setOutputText(result.data.generated_draft);
                setTaxonomy(result.data.taxonomy);
                setLoading(false);
            });
        } catch (error) {
            console.error("Error calling Firebase function:", error);
        }
    };

    const createMarkup = () => {
        return { __html: marked(outputText) };
    };
    console.log("contentType", contentType);
    return (
        <div>
            <div className={styles.container}>
                <div className={styles.boxes}>
                    <div>
                        <textarea
                            className={styles.box}
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Enter any additional instructions"
                        />
                        Content Type:{" "}
                        <select
                            className={styles.selectBox}
                            value={contentType}
                            onChange={(e) => setContentType(e.target.value)}
                        >
                            <option value="gs://anc-pg-hack-defra-cm.appspot.com/content_type_policies_example - detailed guide.pdf">
                                Detailed Guide Content Type Example
                            </option>
                            <option value="Type Bbbbb">Type B</option>
                            <option value="Type Cccccc">Type C</option>
                        </select>
                    </div>
                    <div>
                        <div
                            className={styles.output_box}
                            dangerouslySetInnerHTML={createMarkup()}
                        ></div>
                        <div className={styles.taxonomy}>
                            Taxonomy suggestions: <br />
                            {taxonomy}
                        </div>
                    </div>
                </div>
            </div>
            <div></div>
            <div className={styles.container_submit}>
                <input
                    type="file"
                    className={styles.upload_button}
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                />
                <button
                    className={styles.button}
                    onClick={handleSubmit}
                    disabled={loading}
                >
                    {loading ? "Loading..." : "Submit"}
                </button>
            </div>
        </div>
    );
}

export default TextGen;
