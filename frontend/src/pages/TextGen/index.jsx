import React, { useState } from "react";
import styles from "./TextGen.module.css";
import { getFunctions, httpsCallable } from "firebase/functions";
import { marked } from "marked";
import { getStorage, ref, uploadBytes, getDownloadURL } from "firebase/storage";

function TextGen() {
    const [inputText, setInputText] = useState("");
    const [outputText, setOutputText] = useState("");
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [promptUsed, setPromptUsed] = useState("");

    const functions = getFunctions();
    const storage = getStorage();

    const bucketName = "example_docs";

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

            generateDocuments({ request: inputText, fileUrl: fileUrl }).then(
                (result) => {
                    console.log(result.data);
                    setOutputText(result.data.generated_draft);
                    setLoading(false);
                }
            );
        } catch (error) {
            console.error("Error calling Firebase function:", error);
        }
    };

    const createMarkup = () => {
        return { __html: marked(outputText) };
    };

    return (
        <div>
            <div className={styles.container}>
                <div className={styles.boxes}>
                    <textarea
                        className={styles.box}
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="Enter text"
                    />
                    <div
                        className={styles.output_box}
                        dangerouslySetInnerHTML={createMarkup()}
                    ></div>
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
