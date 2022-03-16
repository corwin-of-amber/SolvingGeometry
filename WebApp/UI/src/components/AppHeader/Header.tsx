import React from 'react';
import './Header.css';
import { BiCategoryAlt } from "react-icons/bi";

export const Header = () => {

    return (
        <div className="header-container">
            <div className='app-logo-container'>
                {React.createElement(BiCategoryAlt, {style:{width:"30px",height:"30px", padding:"10px", color:"white"}})}
                <h1 className='app-header'>Solving Geometry</h1>
            </div>
        </div>
    );
}