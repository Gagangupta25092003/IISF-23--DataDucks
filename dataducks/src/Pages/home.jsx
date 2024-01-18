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

  useEffect(() => {}, []);

  return (
    <div>
      <StickyNavbar Data={data} ChangeData={handleChangeVariable} />
      <FilterComponent Data={data} ChangeData={handleChangeVariable} />
      <div className="bg-transparent flex justify-center"></div>
      <div className="w-screen px-10 py-10">
        <ul className="flex flex-col items-center">
          {data.map((item, id) => (
            <div key={id} className="w-5/6">
              <div className="py-2 px-5  hover:bg-blue-900/50 text-black text-md flex flex-row font-medium font=sm items-center my-1 border border-black rounded-full">
                <div className="font-bold w-96">
                  {item.file_name}
                </div>
                <div className="w-64">Type: {item.file_type}</div>
                <div className="w-64">
                  Size: {(item.file_size / (1024 * 1024)).toFixed(2)}mb
                </div>
                <div className="w-72">Last Modified: {item.creation_date} </div>
              </div>
            </div>
          ))}
        </ul>
      </div>
    </div>
  );
}
