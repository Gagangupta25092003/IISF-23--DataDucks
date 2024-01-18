import React, { useState, useEffect } from "react";
import { PieChart, Pie, ResponsiveContainer, Cell, Legend } from "recharts";
import MapWithGeoJSON from "../components/Preview_GeoJson";
const Bullet = ({ backgroundColor, size }) => {
  return (
    <div
      className="CirecleBullet"
      style={{
        backgroundColor,
        width: size,
        height: size,
      }}></div>
  );
};

const CustomizedLegend = (props) => {
  const { payload } = props;
  return (
    <ul className="LegendList">
      {payload.map((entry, index) => (
        <li key={`item-${index}`}>
          <div className="BulletLabel flex items-center">
            <Bullet backgroundColor={entry.payload.fill} size="10px" />
            <div className="BulletLabelText ml-2">{entry.value} :</div>
            <div style={{ marginLeft: "20px" }}>{entry.payload.value}</div>
          </div>
        </li>
      ))}
    </ul>
  );
};

export function Analytics() {
  const [totalFiles, setTotalFiles] = useState(0);
  const [filetypeslen, setFileTypesLen] = useState(0);
  const [filetypes, setFileTpes] = useState([]);
  const [filetypesdist, setFileTpesDist] = useState([0, 0, 0, 0]);
  const [maxsize, setMax] = useState(0);
  const [minsize, setMin] = useState(0);
  const [size0, setSize0] = useState(10);
  const [size1, setSize1] = useState(20);
  const [size2, setSize2] = useState(11);
  const [size3, setSize3] = useState(5);
  const [type0, settype0] = useState(10);
  const [type1, settype1] = useState(20);
  const [type2, settype2] = useState(11);
  const [type3, settype3] = useState(5);

  const [data, setData] = useState([
    { name: "GeoJson Types", students: 0 },
    { name: "Tiff Types", students: 0 },
    { name: "Las Types", students: 0 },
    { name: "Others", students: 0},
  ]);

  const [dataPie, setDataPie] = useState([
    { name: "<1mb", students: 2 },
    { name: "1-10mb", students: 2 },
    { name: "10-100mb", students: 2 },
    { name: ">100mb", students: 2 },
  ]);
  

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
    index,
  }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central">
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  // const fetchData = async () => {
  //   try {
  //     const response = await fetch("http://localhost:5000/analytics");
  //     const jsonData = await response.json();
  //     console.log("Getting Analytics");
  //     console.log(jsonData);
  //     setTotalFiles(jsonData.total_files);
  //     setFileTpes(jsonData.file_types);
  //     setFileTypesLen(jsonData.file_types_len);
  //     setMax(jsonData.max);
  //     setMin(jsonData.min);
  //     setSize0(jsonData.size0);
  //     setSize1(jsonData.size1);
  //     setSize2(jsonData.size2);
  //     setSize3(jsonData.size3);
  //     setFileTpesDist(jsonData.file_type_distribution);
  //     console.log(jsonData.file_type_distribution);
  //   } catch (error) {
  //     console.error("Error fetching data:", error);
  //   }
  // };

  // const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:5000/analytics");
        const jsonData = await response.json();
        console.log("Getting Analytics");
        console.log(jsonData);
        setTotalFiles(jsonData.total_files);
        setFileTpes(jsonData.file_types);
        setFileTypesLen(jsonData.file_types_len);
        setMax(jsonData.max);
        setMin(jsonData.min);
        setSize0(jsonData.size0);
        setSize1(jsonData.size1);
        setSize2(jsonData.size2);
        setSize3(jsonData.size3);
        settype0(jsonData.file_type_distribution[0]);
        settype1(jsonData.file_type_distribution[1]);
        settype2(jsonData.file_type_distribution[2]);
        settype3(jsonData.file_type_distribution[3]);
        setFileTpesDist(jsonData.file_type_distribution);
  
        // Update the pie chart data after setting the state
        const newData = [
          { name: "GeoJson Types", students: type0 },
          { name: "Tiff Types", students: type1 },
          { name: "Las Types", students: type2 },
          { name: "Others", students: type3 },
        ];
        await setData(newData);
  
        const newDataPie = [
          { name: "<1mb", students: size0 },
          { name: "1-10mb", students: size1 },
          { name: "10-100mb", students: size2 },
          { name: ">100mb", students: size3 },
        ];
        await setDataPie(newDataPie);
  
        console.log("newData", newData);
        console.log(newDataPie);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
    fetchData();
}, []); 

  

  return (
    <div className="px-16 py-8 text-lg text-blue-800 bg-gray-100">
      <div className="mb-16 flex flex-col items-center">
        <div className="text-5xl font-bold mb-8">
          Analytics of DataDucks DataBase
        </div>
        <div>Total No. of F﻿ iles = {totalFiles}</div>
        <div>Total No. of Types of Files Present = {filetypeslen}</div>
        <div>
          <ul>
            {filetypes.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
        <div>Maximum Size File Present = {maxsize / (1024 * 1024)} mb</div>
        <div>Minimum Size File Present = {minsize / (1024 * 1024)} mb</div>
      </div>
      <div className="flex">
        <div className="flex flex-col items-center justify-center w-1/2">
          <p className="text-3xl mb-8 font-bold">Files Type Distribution</p>

          <PieChart width={600} height={600}>
            <Pie
              data={data}
              // cx="50%"
              // cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={200}
              fill="#8884d8"
              dataKey="students">
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Legend content={<CustomizedLegend />} />
          </PieChart>

          {/* <Example/> */}
        </div>

        <div className="flex flex-col items-center justify-center w-1/2">
          <p className="text-3xl mb-8 font-bold ">Files Size Distribution</p>
          <PieChart width={600} height={600}>
            <Pie
              data={dataPie}
              // cx="50%"
              // cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={200}
              fill="#8884d8"
              dataKey="students">
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Legend content={<CustomizedLegend />} />
          </PieChart>
        </div>
      </div>

      {/* <GeoJSONPreview geojsonPath="/home/skycoder/Music/untitledfolder/geojson1.geojson"/> */}
    </div>
  );
}
