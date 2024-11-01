import React, { useState } from "react";
import styles from "./Tabs.module.css";
import TextGen from "../../pages/TextGen";
import {Search} from "../../pages/Search";

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
                    className={
                        activeTab === "vertexSearch" ? styles.active : ""
                    }
                    onClick={() => {
                        setActiveTab("vertexSearch");
                    }}
                >
                    Vertex Search
                </button>
            </div>

            <div className="outlet">
                {activeTab === "textGen" && <TextGen />}
                {activeTab === "vertexSearch" && <Search />}
            </div>
        </div>
    );
};

export default Tabs;
