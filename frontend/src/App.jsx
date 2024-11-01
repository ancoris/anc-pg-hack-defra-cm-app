import React, { useState } from "react";
import "./App.css";
import { initializeApp } from "firebase/app";
import Tabs from "./components/Tabs";

const firebaseConfig = {
    apiKey: "AIzaSyATz8A_GAg8vW5YJ5N7AlvLjLryHKv_hcw",
    authDomain: "anc-pg-hack-defra-cm.firebaseapp.com",
    projectId: "anc-pg-hack-defra-cm",
    storageBucket: "anc-pg-hack-defra-cm.appspot.com",
    messagingSenderId: "837986133504",
    appId: "1:837986133504:web:6e965e75aa964eddcddae5"
  };

initializeApp(firebaseConfig);

function App() {

    return (
        <>
            <Tabs />
        </>
    );
}

export default App;
