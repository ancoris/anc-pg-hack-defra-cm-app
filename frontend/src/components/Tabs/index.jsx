import React, { useState } from "react";
import styles from "./Tabs.module.css";
import TextGen from "../../pages/TextGen";

const Tabs = () => {
    const [activeTab, setActiveTab] = useState("textGen");

    return (
        <div className={styles.tabsContainer}>
            <div className={styles.tabsWrapper}>
                <button
                    className={activeTab === "textGen" ? styles.active : ""}
                    onClick={() => {
                        setActiveTab("textGen");
                    }}
                >
                    Text Generation
                </button>
                <button
                    className={activeTab === "taxonomy" ? styles.active : ""}
                    onClick={() => {
                        setActiveTab("taxonomy");
                    }}
                >
                    Taxonomy
                </button>
            </div>

            <div className="outlet">
                {activeTab === "textGen" && <TextGen />}
                {activeTab === "taxonomy" && <h1>Taxonomy</h1>}
            </div>
        </div>
    );
};

export default Tabs;
