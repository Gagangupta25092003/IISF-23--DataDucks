import { React, useEffect, useState } from "react";
import { StickyNavbar } from "../components/navbar";
import { Button, Card } from "@material-tailwind/react";
import { Link } from "react-router-dom";
import ImageIcon from "../resources/Images/location.png";
import DownloadIcon from "../resources/Images/downloads.png";
import FilterComponent from "../components/filter";
export function Home() {
  const [data, setData] = useState([]);

  const handleChangeVariable = (newValue) => {
    setData(newValue);
    console.log("Data", data);
  };

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       console.log("Starting to get Data");
  //       const response = await fetch("http://localhost:5000/get_database");
  //       console.log("response", response);
  //       const result = await response.json();
  //       setData(result);
  //       console.log(data);
  //       await sleep(2000);
  //     } catch (error) {
  //       console.log("Error in fetching Data: ", error);
  //     }
  //   };
    
    // fetchData();

  // }, []);

  return (
    <div>
      <StickyNavbar Data={data} ChangeData = {handleChangeVariable}/>
      <FilterComponent />
      <div className="bg-transparent flex justify-center"></div>
      <div className="w-screen px-10 py-10">
        <ul className="flex flex-wrap">
          {data.map((item, id) => (
            <div
              key={id}
              className="w-full sm:w-1/2 md:w-1/3 lg:w-1/4 p-4">
              <Card className="py-4 px-5 bg-blue-800 hover:bg-blue-900/50 text-black text-md h-56 sm:h-64 md:h-60 rounded-lg">
                <img
                  className="mx-auto w-24 "
                  src={ImageIcon}
                  alt="Centered Image"
                />
                <p className="font-medium text-lg mx-auto">{item.file_name}</p>
                <div className="flex flex-wrap justify-between">
                  <div>Type: {item.file_type}</div>
                  <div>
                    Size: {Math.round(item.size / 1024)}mb &nbsp; &nbsp;&nbsp;
                  </div>
                  <div className="flex">
                    <img
                      className="w-4 h-4 my-auto"
                      src={DownloadIcon}
                      alt="Centered Image"
                    />{" "}
                    &nbsp;10
                  </div>
                </div>
                <p>Last Modified: {item.creation_date} </p>

                <p>Tags:</p>
              </Card>
            </div>
          ))}
        </ul>
      </div>
    </div>
  );
}
