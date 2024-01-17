import { Button } from "@material-tailwind/react";
import React, { useState, useEffect } from "react";
import { Link } from 'react-router-dom';
// import APIService from "../components/api_service";
// import fetch from 'node-fetch';

export function InputDirectory() {
  const [inputString, setInputString] = useState("");
  const [history, setHistory] = useState("");
  const [loadingState, setLoadingState] = useState(false);
  console.log("Running...");
  const insert_dir = () => {
    setLoadingState(true);
    setTimeout(() => {
      console.log("1 second passed");
      console.log("Adding Directory: ", inputString);
      const requestBody = {
        dir_path: inputString,
      };
      return fetch(`http://localhost:5000/upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })
        .then((response) => response.json())
        .then((data) => {
          // Handle the data
          console.log(data);
          const jsonResponse = JSON.parse(JSON.stringify(data));

            // Access the data of a specific key
            const keyData = jsonResponse.key;

            setHistory(keyData);
        })
        .catch((error) => {
          console.log(error);
          console.log("Error in Response");
        })
        .finally(setLoadingState(false));
    }, 1000);
  };

  //   const sendStringToServer = async () => {
  //     try {
  //         console.log("Clicked Submitted Button");
  //         const js_file = JSON.stringify({ input_string: inputString });
  //         console.log(js_file);
  //         const response = await fetch("http://localhost:5000/upload", {
  //         method: "POST",
  //         headers: {
  //           "Content-Type": "application/json",
  //         },
  //         body: js_file,
  //       });

  //       if (response.ok) {
  //         const result = await response.json();
  //         console.log("Done uploading");
  //         console.log(result.message);
  //       } else {
  //         console.error("Failed to send string to server");
  //       }
  //     } catch (error) {
  //       console.error("Error:", error);
  //     }
  //   };

  return (
    <div>
      <div className="text-white text-3xl w-full flex items-center justify-center mt-10 z-1 absolute font-bold">
        Dataducks
      </div>
      {!loadingState && (
        <div>
        <div className="flex items-center h-screen">
          <div className="w-full m-10">
            <form className="lg:flex lg:space-x-3 -mt-40">
              <label
                htmlFor="fileDirectory"
                className="block text-white lg:my-0 my-2">
                Enter Dataset Folder Path:
              </label>

              <input
                type="text"
                className="lg:my-0 my-2 block p-4 ps-10 text-sm text-gray-900 border border-gray-300 rounded-full bg-gray-50 hover:border-[#5210ad] w-full"
                id="fileDirectory"
                name="fileDirectory"
                placeholder="e.g., /path/to/your/directory"
                required
                value={inputString}
                onChange={(e) => setInputString(e.target.value)}
              />
              <button
                type="button"
                className="lg:my-0 my-2 text-white bg-[#285180] hover:bg-[#5210ad] focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-full text-lg px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                onClick={insert_dir}>
                Upload
              </button>
            </form>
            <div className="text-xl flex items-center justify-center text-gray-500 mt-10">
                {history}
            </div>
            <div className="text-xl flex items-center justify-center mt-5">
                <Button className="text-white bg-[#285180] hover:bg-[#5210ad] focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-full text-lg px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                <Link to="/database">Go back to DataBase</Link>
                </Button>
            </div>
          </div>
        </div>
        
        </div>
      )}
      {loadingState && <div className="bg-transparent z-30 flex items-center justify-center h-screen">
        
        
        <div role="status">
            <svg aria-hidden="true" class="w-20 h-20 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
                <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
            </svg>
            <span class="sr-only">Loading...</span>
        </div>

        </div>}
    </div>
  );
}
