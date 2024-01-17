import React from "react";
import { Link } from "react-router-dom";
import {
  Navbar,
  MobileNav,
  Typography,
  Button,
  IconButton,
  Card,
  Collapse
} from "@material-tailwind/react";

export function StickyNavbar() {
  const [openNav, setOpenNav] = React.useState(false);

  React.useEffect(() => {
    window.addEventListener(
      "resize",
      () => window.innerWidth >= 960 && setOpenNav(false)
    );
  }, []);

  const navList = (
    <ul className="mt-2 mb-4 flex flex-col gap-2 lg:mb-0 lg:mt-0 lg:flex-row lg:items-center lg:gap-6 ms-2">
      
      <Typography as="li" variant="small" className="p-1 font-normal">
          <Link to="/" className="flex items-center hover:text-blue-900"> About </Link>         
      </Typography>
      <Typography as="li" variant="small" className="p-1 font-normal">
          <Link to="/database" className="flex items-center hover:text-blue-900"> DataBase </Link>        
      </Typography>
      
    </ul>
  );

  return (
    <div className=" max-h-[768px] w-full  pb-0 m-0 bg-transparent">
      <nav className="sticky top-0 z-10 h-max max-w-full rounded-none px-4 py-2 lg:px-8 lg:py-4 bg-transparent">
        <div className="flex-nowrap items-center justify-between text-blue-800 mg:flex">
          <div className="mr-5  justify-between flex items-center">
            <Typography
              as="a"
              href="#"
              className="cursor-pointer py-1.5 font-black text-3xl w-max hover:text-blue-900">
              DataDucks{" "}
              <span className=" text-sm/[10px]">
                (Intelligent Data Catalouging System)
              </span>
            </Typography>
            
            <div className="flex items-center gap-4 w-fit">
            <div className="mx-4 hidden lg:block text-[#22227b]  w-max">
              {navList}
            </div>
            <Button className="text-white bg-blue-800 hover:bg-blue-900 focus:ring-4 focus:outline-none focus:ring-blue-300  rounded-full  px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
              <Link to="/upload_directory">Upload Directory</Link>
            </Button>
            <IconButton
              variant="text"
              className=" ml-auto h-6 w-6 text-inherit hover:bg-transparent focus:bg-transparent active:bg-transparent lg:hidden"
              ripple={false}
              onClick={() => setOpenNav(!openNav)}>
              {openNav ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </IconButton>
            
          </div>
          </div>
          <Collapse className="text-[#22227b] " open={openNav}>
          {navList}
          <div className="flex items-center gap-x-1"></div>
        </Collapse>
         
          <div className="w-full">
            <form>
              <label
                clasName="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white">
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none rounded-full">
                  <svg
                    className="w-4 h-4 text-gray-500 dark:text-gray-400"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 20 20">
                    <path
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
                    />
                  </svg>
                </div>
                <input
                  type="search"
                  id="default-search"
                  className="block p-4 ps-10 text-sm text-gray-900 border border-gray-300 rounded-full bg-[#07255021] hover:border-[#5210ad] w-full"
                  placeholder="Search for Dataset"
                  required
                />
                <button
                  type="submit"
                  className="text-white absolute end-2.5 bottom-2.5 bg-blue-800 hover:bg-blue-900 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-full text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                    Search
                </button>
              </div>
            </form>
          </div>
          
        </div>
        
      </nav>
    </div>
    
  );
}
