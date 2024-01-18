import React from "react";

export function Analytics() {
    
    const [totalFiles, setTotalFiles] = useState(0);
    const [filetypeslen, setFileTypesLen] = useState(0);
    const [filetypes, setFileTpes] = useState([]);
    const [maxsize, setMax] = useState(0);
    const [minsize, setMin] = useState(0);
    const [size0, setSize0] = useState(0);
    const [size1, setSize1] = useState(0);
    const [size2, setSize2] = useState(0);
    const [size3, setSize3] = useState(0);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:5000/analytics');
      const jsonData = await response.json();
      setTotalFiles(jsonData.totak_files);
      setFileTpes(jsonData.file_types);
      setFileTypesLen(jsonData.file_types_len);
      setMax(jsonData.max);
      setMin(jsonData.min);
      setSize0(jsonData.size0);
      setSize1(jsonData.size1);
      setSize2(jsonData.size2);
      setSize3(jsonData.size3);

    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  return (
    <div className="m-16 text-lg text-blue-800">
      <div className="text-3xl text-bold">Analytics of DataDucks DataBase</div>
      <div>Total No. of Files = {totalFiles}</div>
      <div>Total No. of Types of Files Present = {filetypeslen}</div>
      <div>
        <ul>
          {filetypes.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>
      <div>MaxSize = {Maxsize/(1024*1024)} mb</div>
      <div>MinSize = {MinSize/(1024*1024)} mb</div>
      <div>less than 1mb = {size0}</div>
      <div>1-10mb = {size1}</div>
      <div>10-100mb = {size2}</div>
      <div>greater than 100mb = {size3}</div>

      <div>

      </div>
    </div>
  );
}
