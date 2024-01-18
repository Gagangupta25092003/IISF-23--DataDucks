import React from "react";

export function Analytics() {
  return (
    <div>
      <div>Analytics of DataDucks DataBase</div>
      <div>Total No. of Files = {totalFiles}</div>
      <div>Total No. of Types of Files Present = {filetypeslen}</div>
      <div>
        <ul>
          {myArray.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>
      <div>MaxSize = {}/div>

      <div>

      </div>
    </div>
  );
}
