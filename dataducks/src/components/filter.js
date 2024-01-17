import React, { useState } from 'react';
import downicon from "../resources/Images/arrow_down.png"

const FilterComponent = () => {
  const [showFilters, setShowFilters] = useState(false);

  const handleButtonClick = () => {
    setShowFilters(!showFilters);
  };

  return (
    <div>
      <div className="bg-gray-100 hover:bg-gray-200 text-blue-900 px-4 flex mx-auto border-b border-blue-900" onClick={handleButtonClick}>
        <img src={downicon} className='w-6 h-6 my-auto'/>&nbsp;&nbsp;
        <h1 className="text-xl font-medium  mb-2"> Filters</h1>

      </div>
      {showFilters && (
        <div className=" p-4 text-blue-900 bg-gray-100 px-12">

          {/* Size Filter */}
          <div className="mb-4 ">
            <h3 className="text-lg font-medium ">Size</h3>
            <div className="flex flex-wrap gap-2">
              <label>
                <input type="number" className="mr-2 w-16 border-b border-blue-900" placeholder=' in mb'/>
                min
              </label>
              <label>
                <input type="number" className="mr-2 w-16 border-b border-blue-900" placeholder=' in mb'/>
                max
              </label>
            </div>
          </div>

          {/* File Type Filter */}
          <div className="mb-4">
            <h3 className="text-lg font-bold font-medium ">File Type</h3>
            <div className="flex flex-wrap gap-2">
              <label>
                <input type="checkbox" className="mr-2" />
                las
              </label>
              <label>
                <input type="checkbox" className="mr-2" />
                tiff
              </label>
              <label>
                <input type="checkbox" className="mr-2" />
                geojson
              </label>
              <label>
                <input type="checkbox" className="mr-2" />
                las
              </label>
              <label>
                <input type="checkbox" className="mr-2" />
                tiff
              </label>
              <label>
                <input type="checkbox" className="mr-2" />
                geojson
              </label>
            </div>
            <button className='bg-blue-800 w-24 text-lg text-white rounded-full hover:bg-blue-900 mt-4'>
                Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterComponent;
