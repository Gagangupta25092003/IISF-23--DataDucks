import React from "react";
import { StickyNavbar } from "../components/navbar";
import { Button } from "@material-tailwind/react";
import { Link } from 'react-router-dom';

export function Home() {
    return(
    <div>
        <StickyNavbar/>
        <div className="bg-transparent flex justify-center">
        <Button className="text-white bg-[#285180] hover:bg-[#5210ad] focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-full text-lg px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                <Link to="/upload_directory">Upload Directory</Link>
                </Button>
        </div>
    </div>);
}